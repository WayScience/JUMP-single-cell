suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(ggplot2))
suppressPackageStartupMessages(library(patchwork))

# Load variables important for plotting (e.g., themes, phenotypes, etc.)
source("themes.r")

# Set directory for data split
data_split_dir <- file.path("./results/Mito_JUMP_zernike_features")
# File structure in dir
umap_files <- list.files(data_split_dir, full.names = TRUE)
print(umap_files)

output_fig_dir <- file.path("figures/Mito_JUMP_zernike_features")
umap_prefix <- "Mito_JUMP_zernike_features_"
umap_suffix <- ".tsv"

# Define output figure paths as a dictionary where each plate has a figure output path
output_umap_files <- list()
for (umap_file in umap_files) {
    # Use the file name to extract plate
    file_name <- basename(umap_file)
    plate <- gsub(umap_suffix, "", gsub(umap_prefix, "", file_name))

    output_umap_files[[plate]] <- file.path(output_fig_dir, paste0(umap_prefix, plate))
}
        
print(output_umap_files)

# Load data
umap_cp_df <- list()
for (plate in names(output_umap_files)) {
    # Find the umap file associated with the plate
    umap_file <- umap_files[stringr::str_detect(umap_files, plate)]
    
    # Load in the umap data
    df <- readr::read_tsv(
        umap_file,
        col_types = readr::cols(
            .default = "d",
            "Metadata_data_name" = "c",
            "Metadata_Predicted_Class" = "c",
            "Metadata_Phenotypic_Value" = "n"
        )
    ) %>%
    # Generate a new column that we will use for plotting
    # Note, we define focus_phenotypes in themes.r
    dplyr::mutate(Metadata_Plot_Label = if_else(
        Metadata_Predicted_Class %in% focus_phenotypes,
        Metadata_Predicted_Class,
        "Other"
    ))

    df$Metadata_Predicted_Class <-
        dplyr::recode_factor(df$Metadata_Predicted_Class, !!!focus_phenotype_labels)

    # Append the data frame to the list
    umap_cp_df[[plate]] <- df 
}

# print example of loaded in file
head(df)

for (plate in names(umap_cp_df)) {
    # Focus phenotypic class UMAP file path
    output_file <- output_umap_files[[plate]]
    output_file <- paste0(output_file, "_all_phenotypes_UMAP.png")

    # UMAP labelled with focus phenotypic classes
    phenotype_gg <- (
        ggplot(umap_cp_df[[plate]], aes(x = UMAP0, y = UMAP1))
        + geom_point(
            aes(color = Metadata_Predicted_Class), size = 0.4, alpha = 0.5
        )
        + theme_bw()
        + scale_color_manual(
            name = "Phenotypes",
            values = all_phenotype_class_colors
        )
    )

    ggsave(output_file, phenotype_gg, dpi = 500, height = 6, width = 8)
}

for (plate in names(umap_cp_df)) {
    # Focus phenotypic class UMAP file path
    output_file <- output_umap_files[[plate]]
    output_file <- paste0(output_file, "_focused_phenotypes_UMAP.png")

    # UMAP labelled with focus phenotypic classes
    phenotype_gg <- (
        ggplot(umap_cp_df[[plate]], aes(x = UMAP0, y = UMAP1))
        + geom_point(
            aes(color = Metadata_Predicted_Class), size = 0.4, alpha = 0.5
        )
        + theme_bw()
        + scale_color_manual(
            name = "Phenotypes",
            values = focus_phenotype_colors
        )
        # + theme(legend.position = "none")  # Remove the legend
    )

    ggsave(output_file, phenotype_gg, dpi = 500, height = 6, width = 8)
}

# Specify only one model and change file name to show only the data_split
desired_plate <- "final_greg_areashape_model"
output_file_name <- "Mito_JUMP_all_features"

# Check if the plate is the desired one, and run the code only for that plate
if (desired_plate %in% names(umap_cp_df)) {
    plate <- desired_plate

    # Data set name UMAP file path
    output_file <- file.path(output_fig_dir, paste0(output_file_name, "_data_set_label_UMAP.png"))

    # UMAP labelled with data set name
    data_set_gg <- (
        ggplot(umap_cp_df[[plate]], aes(x = UMAP0, y = UMAP1))
        + geom_point(
            aes(color = Metadata_data_name), size = 0.4, alpha = 0.3
        )
        + geom_point(
            data = subset(umap_cp_df[[plate]], Metadata_data_name == "mitocheck"),
            aes(x = UMAP0, y = UMAP1, color = Metadata_data_name),
            size = 0.4, alpha = 0.3
        )
        + theme_bw()
        + scale_color_manual(
            name = "Data set name",
            values = data_set_colors
        )
        + guides(
            shape = guide_legend(override.aes = list(size = 3))
        )
        + theme(
            axis.text = element_text(size = 14),
            axis.title = element_text(size = 16)  # Change the font size here
        )
        + coord_cartesian(xlim = c(-5, 12), ylim = c(-4, 13))  # Set axis limits here
    )

    ggsave(output_file, data_set_gg, dpi = 500, height = 6, width = 8)
}


# Custom function for name repair
name_repair_function <- function(names) {
  names[2] <- paste0(names[2], "_original")
  return(names)
}

for (plate in names(umap_cp_df)) {
    # Focus phenotypic class/data set facet UMAP file path
    output_file <- output_umap_files[[plate]]
    output_file <- paste0(output_file, "_facet_focus_phenotype_data_set_UMAP.png")
    
    umap_focus_df <- umap_cp_df[[plate]] %>% dplyr::filter(Metadata_Predicted_Class %in% focus_phenotypes)

    # add grey points to each facet by duplicating the UMAP coords for 
    df_background <- tidyr::crossing(
        umap_focus_df,
        .name_repair = name_repair_function
    )

    # Facet UMAP labelling phenotype and data set
    umap_facet_phenotype_data_gg <- (
        ggplot(
            umap_cp_df[[plate]] %>% dplyr::filter(Metadata_Plot_Label %in% focus_phenotypes),
            aes(x = UMAP0, y = UMAP1)
        )
        + geom_point(
            data = df_background,
            color = "lightgray",
            size = 0.1,
            alpha = 0.4
        )
        + geom_point(
            aes(color = Metadata_Plot_Label),
            size = 0.1
        )

        + facet_grid("Metadata_data_name~Metadata_Predicted_Class")
        + theme_bw()
        + phenotypic_ggplot_theme
        + guides(
            color = guide_legend(
                override.aes = list(size = 2)
            )
        )
        + labs(x = "UMAP0", y = "UMAP1")
        + scale_color_manual(
            "Phenotype",
            values = focus_phenotype_colors,
            labels = focus_phenotype_labels
        )
    )

    ggsave(output_file, umap_facet_phenotype_data_gg, dpi = 500, height = 4, width = 10)

}
