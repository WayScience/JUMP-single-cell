library(ggplot2)
library(dplyr)

focus_phenotypes <- c(
    "Apoptosis",
    "Elongated",
    "Interphase",
    "Large",
    "Metaphase",
    "OutOfFocus"
)

focus_phenotype_colors <- c(
    "Apoptosis" = "#e7298a",
    "Elongated" = "#1b9e77",
    "Interphase" = "#7570b3",
    "Large" = "#d95f02",
    "Metaphase" = "black",
    "OutOfFocus" = "red",
    "Other" = "grey"
)

focus_phenotype_labels <- c(
    "Apoptosis" = "Apoptosis",
    "Elongated" = "Elongated",
    "Interphase" = "Interphase",
    "Large" = "Large",
    "Metaphase" = "Metaphase",
    "OutOfFocus" = "OutOfFocus",
    "Other" = "Other"
)

facet_labels <- c(
    "compound" = "compound",
    "crispr" = "crispr",
    "orf" = "orf"
)

phenotypic_ggplot_theme <- (
    theme_bw()
    + theme(
        axis.text = element_text(size = 10),
        legend.title = element_text(size = 12),
        legend.text = element_text(size = 10),
        legend.key.height = unit(0.8, "lines"),
        strip.text = element_text(size = 10),
        strip.background = element_rect(
            linewidth = 0.5, color = "black", fill = "#fdfff4"
        )
    )
)

# Vector with all classes and colors assigned
all_phenotype_class_colors <- c(
    "ADCCM" = "#1f77b4",
    "Anaphase" = "#ff7f0e",
    "Apoptosis" = "#2ca02c",
    "Binuclear" = "#d62728",
    "Elongated" = "#9467bd",
    "Grape" = "#8c564b",
    "Hole" = "#e377c2",
    "Interphase" = "#7f7f7f",
    "Large" = "#bcbd22",
    "Metaphase" = "#17becf",
    "MetaphaseAlignment" = "#98df8a",
    "OutOfFocus" = "#ff9896",
    "Polylobed" = "#aec7e8",
    "Prometaphase" = "#f7b6d2",
    "SmallIrregular" = "#c5b0d5"
)

# Vector with each data set name and color
data_set_colors <- c(
    "mitocheck" = "#008000",
    "jump" = "#990099"
)

# # Colors for treatment
treatment_colors <- c(
    "compound" = "#1f77b4",
    "crispr" = "#2ca02c",
    "orf" = "#e377c2"
)

# Define a vector of plate names
plate_names <- c(
    'BR00116995', 'BR00116997', 'BR00117004', 'BR00117055', 'BR00117015', 'BR00116994',
    'BR00117050', 'BR00117051', 'BR00117020', 'BR00118041', 'BR00117024', 'BR00117053',
    'BR00118039', 'BR00117023', 'BR00118048', 'BR00117012', 'BR00117019', 'BR00117010',
    'BR00118049', 'BR00117026', 'BR00116991', 'BR00116999', 'BR00116996', 'BR00117052',
    'BR00117009', 'BR00117016', 'BR00117003', 'BR00116993', 'BR00118050', 'BR00117022',
    'BR00117002', 'BR00117021', 'BR00117025', 'BR00117054', 'BR00117017', 'BR00117008',
    'BR00118047', 'BR00118043', 'BR00118040', 'BR00118045', 'BR00117001', 'BR00117011',
    'BR00117013', 'BR00116998', 'BR00117005', 'BR00117000', 'BR00117006', 'BR00118042',
    'BR00116992', 'BR00118046', 'BR00118044'
)

# Generate unique hex color codes based on plate names
plate_colors <- rainbow(length(plate_names))
