# Barcode Platemap and Platemaps

In this folder, there three file types:

1. **Barcode plate** - CSV file that associates each plate to the correct platemap
2. **Platemap** - TXT that contains the plate layout (e.g., what broad sample is in what well)
3. **Metadata** - TSV file that contains all of the relevant metadata per broad sample
4. **Experimental Metadata** - TSV file that contains additional information about the experiment

The platemap and metadata files are broken down by treatment (e.g., compound, crispr, or orf).

We downloaded metadata files excluding the **Experimental Metadata** from [the metadata folder in AWS](https://cellpainting-gallery.s3.amazonaws.com/index.html#cpg0000-jump-pilot/source_4/workspace/metadata/external_metadata/).
We downloaded the barcode platemap and platemap files from [the platemaps folder in AWS](https://cellpainting-gallery.s3.amazonaws.com/index.html#cpg0000-jump-pilot/source_4/workspace/metadata/platemaps/2020_11_04_CPJUMP1/).
We downloaded the experimental metadata file from [the jump-cellpainting github repo subfolder](https://github.com/jump-cellpainting/2023_Chandrasekaran_submitted/blob/9edd26d60524a62f993d4df40a5d8908206714f5/README.md#batch-and-plate-metadata).

Visualization of the platemaps are as follows:

![compound_platemap](./ex_figures/JUMP_compound_platemap.png)
> Platemap for compound treatments

![crispr_platemap](./ex_figures/JUMP_crispr_platemap.png)
> Platemap for crispr treatments

![orf_platemap](./ex_figures/JUMP_orf_platemap.png)
> Platemap for orf treatments
