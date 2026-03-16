from __future__ import annotations

import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import urlparse

import pandas as pd
import s3fs


# Lightweight containers used to track per-file work and overall outcomes.
@dataclass(frozen=True)
class DownloadJob:
    """Single download task mapping one S3 URL to one local file path."""

    s3_url: str
    local_path: Path


@dataclass(frozen=True)
class DownloadSummary:
    """Aggregate counts and error details from a download run."""

    total_jobs: int
    downloaded: int
    skipped: int
    failed: int
    failures: List[Tuple[DownloadJob, str]]


def validate_column(df: pd.DataFrame, column_name: str, kind: str) -> None:
    """Ensure a required dataframe column exists."""

    if column_name not in df.columns:
        raise ValueError(f"{kind} column not found: {column_name}")


def s3_url_to_remote_path(s3_url: str) -> str:
    """Convert an ``s3://`` URL into the ``bucket/key`` form expected by s3fs."""

    parsed = urlparse(s3_url)
    if parsed.scheme != "s3" or not parsed.netloc or not parsed.path:
        raise ValueError(f"Invalid S3 URL: {s3_url}")
    return f"{parsed.netloc}{parsed.path}"


def build_jobs(
    df: pd.DataFrame,
    url_column: str,
    output_dir_column: Optional[str] = None,
    default_output_dir: Path = Path("downloaded_jump_pilot_images"),
    max_files: Optional[int] = None,
) -> List[DownloadJob]:
    """Create validated download jobs from metadata columns in a dataframe."""

    # Build a clean, de-duplicated download plan from dataframe metadata.
    validate_column(df, url_column, "URL")
    if output_dir_column is not None:
        validate_column(df, output_dir_column, "Output directory")

    cols = [url_column]
    if output_dir_column is not None:
        cols.append(output_dir_column)

    jobs_df = df[cols].copy()
    jobs_df = jobs_df.dropna(subset=[url_column])
    jobs_df[url_column] = jobs_df[url_column].astype(str).str.strip()
    jobs_df = jobs_df[jobs_df[url_column].str.lower().str.endswith(".tiff")]

    if output_dir_column is not None:
        jobs_df = jobs_df.dropna(subset=[output_dir_column])
        jobs_df[output_dir_column] = jobs_df[output_dir_column].astype(str).str.strip()
        jobs_df = jobs_df[jobs_df[output_dir_column] != ""]

    jobs_df = jobs_df.drop_duplicates(subset=[url_column]).reset_index(drop=True)

    jobs: List[DownloadJob] = []
    for _, row in jobs_df.iterrows():
        s3_url = row[url_column]
        filename = Path(urlparse(s3_url).path).name

        if output_dir_column is not None:
            local_dir = Path(row[output_dir_column])
        else:
            local_dir = default_output_dir

        local_path = local_dir / filename
        jobs.append(DownloadJob(s3_url=s3_url, local_path=local_path))

    if max_files is not None:
        jobs = jobs[:max_files]

    return jobs


def download_one(
    fs: s3fs.S3FileSystem,
    job: DownloadJob,
    overwrite: bool = False,
) -> Tuple[str, DownloadJob, Optional[str]]:
    """Download one image and return status, job, and optional error message."""

    # Download a single file and return a status tuple for aggregation.
    try:
        job.local_path.parent.mkdir(parents=True, exist_ok=True)
        if job.local_path.exists() and not overwrite:
            return ("skipped", job, None)

        remote = s3_url_to_remote_path(job.s3_url)
        with fs.open(remote, "rb") as src, open(job.local_path, "wb") as dst:
            shutil.copyfileobj(src, dst, length=1024 * 1024)

        return ("downloaded", job, None)
    except Exception as exc:  # noqa: BLE001
        return ("failed", job, str(exc))


def download_images_with_metadata(
    df: pd.DataFrame,
    url_column: str,
    output_dir_column: Optional[str] = None,
    default_output_dir: Path = Path("downloaded_jump_pilot_images"),
    workers: int = 4,
    parallel: bool = True,
    max_files: Optional[int] = None,
    overwrite: bool = False,
    dry_run: bool = False,
    verbose: bool = True,
) -> DownloadSummary:
    """Download TIFF images listed in a dataframe and report run statistics."""

    # Orchestrate validation, planning, optional preview, and file transfer execution.
    if workers < 1:
        raise ValueError("workers must be >= 1")
    if not parallel and workers > 1:
        raise ValueError("workers cannot be > 1 when parallel=False")

    jobs = build_jobs(
        df=df,
        url_column=url_column,
        output_dir_column=output_dir_column,
        default_output_dir=Path(default_output_dir),
        max_files=max_files,
    )

    if verbose:
        print(f"Rows in dataframe: {len(df):,}")
        print(f"Unique TIFF files to process: {len(jobs):,}")

    if dry_run:
        # Preview planned transfers without writing any files.
        if verbose:
            for job in jobs[:20]:
                print(f"[DRY RUN] {job.s3_url} -> {job.local_path}")
            if len(jobs) > 20:
                print(f"[DRY RUN] ... and {len(jobs) - 20} more")
        return DownloadSummary(
            total_jobs=len(jobs),
            downloaded=0,
            skipped=0,
            failed=0,
            failures=[],
        )

    fs = s3fs.S3FileSystem(anon=True)

    downloaded = 0
    skipped = 0
    failed = 0
    failures: List[Tuple[DownloadJob, str]] = []

    # Execute downloads in parallel or serial mode, then aggregate results.
    if parallel:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(download_one, fs, job, overwrite) for job in jobs]
            for index, future in enumerate(as_completed(futures), start=1):
                status, job, error = future.result()
                if status == "downloaded":
                    downloaded += 1
                elif status == "skipped":
                    skipped += 1
                else:
                    failed += 1
                    failures.append((job, error or "Unknown error"))
                    if verbose:
                        print(f"[FAILED] {job.s3_url} -> {job.local_path}\n  {error}")

                if verbose and (index % 200 == 0 or index == len(jobs)):
                    print(
                        f"Progress {index:,}/{len(jobs):,} "
                        f"(downloaded={downloaded:,}, skipped={skipped:,}, failed={failed:,})"
                    )
    else:
        for index, job in enumerate(jobs, start=1):
            status, job, error = download_one(fs, job, overwrite)
            if status == "downloaded":
                downloaded += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
                failures.append((job, error or "Unknown error"))
                if verbose:
                    print(f"[FAILED] {job.s3_url} -> {job.local_path}\n  {error}")

            if verbose and (index % 200 == 0 or index == len(jobs)):
                print(
                    f"Progress {index:,}/{len(jobs):,} "
                    f"(downloaded={downloaded:,}, skipped={skipped:,}, failed={failed:,})"
                )

    if verbose:
        print("Done.")
        print(f"Downloaded: {downloaded:,}")
        print(f"Skipped:    {skipped:,}")
        print(f"Failed:     {failed:,}")

    return DownloadSummary(
        total_jobs=len(jobs),
        downloaded=downloaded,
        skipped=skipped,
        failed=failed,
        failures=failures,
    )
