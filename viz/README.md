# Visualization Outputs for PhD Application

**Project:** AI for Landscape Ecology - PREDICTS × Major TOM Analysis
**Generated:** 2025-10-13
**Purpose:** PhD Application for SUSTAIN CDT Project A3137

---

## Generated Figures

### Figure 1: The Challenge - Temporal Gap
**Files:**
- `figure1_temporal_gap.pdf` (36 KB, vector)
- `figure1_temporal_gap.png` (203 KB, preview)

**Description:**
Timeline visualization showing the temporal coverage mismatch between PREDICTS biodiversity data (1992-2018, peak 2000-2010) and Major TOM satellite embeddings (2016-2024, Sentinel-2 era). Highlights the fundamental challenge: only 216 sites (1.4%) fall within the overlap period (2016-2018), while 15,414 sites (98.6%) fall in the temporal gap.

**Key Insights:**
- PREDICTS peak coincides with pre-Sentinel era (2000-2010)
- Sentinel-2 launch (June 2015) creates hard boundary for Major TOM data
- Overlap period (2016-2018) provides minimal training data
- Justifies space-for-time substitution approach

---

### Figure 2: The Data - Spatial Distribution & Coverage
**Files:**
- `figure2_spatial_distribution.pdf` (505 KB, vector)
- `figure2_spatial_distribution.png` (923 KB, preview)

**Description:**
Global map showing distribution of 15,622 matched PREDICTS agricultural sites overlaid on Major TOM 10km grid. Sites color-coded by sampling year (red: older, green: recent) using RdYlGn colormap. Demonstrates global coverage across all continents with concentrations in tropical regions, Europe, and North America.

**Key Insights:**
- Global coverage spanning 6 continents
- High density in: Brazil, UK, Southeast Asia, Sub-Saharan Africa
- Color gradient shows temporal progression
- Mean matching distance: 32.3 km
- Land use composition: Cropland (majority), Pasture, Plantation forest

**Technical Details:**
- Projection: Robinson (equal-area)
- Coordinate system: WGS84 (EPSG:4326)
- Natural Earth features for coastlines and borders

---

### Figure 4: The Quality - Matching Statistics
**Files:**
- `figure4_matching_statistics.pdf` (404 KB, vector)
- `figure4_matching_statistics.png` (1.1 MB, preview)

**Description:**
Three-panel analysis quantifying matching quality between PREDICTS sites and Major TOM patches:

**Panel A: Distance Distribution Histogram**
- Shows distribution of distances from PREDICTS sites to nearest Major TOM patch
- Threshold annotations at 10, 20, 30 km
- Mean distance: 32.33 km, Median: 30.54 km

**Panel B: Cumulative Distribution Function**
- Shows percentage of sites within each distance threshold
- 6.2% of sites within 10 km
- 22.4% within 20 km
- 48.7% within 30 km

**Panel C: Distance vs Temporal Lag Scatter**
- Shows trade-off between spatial and temporal matching
- Color-coded by land use type (Cropland: green, Pasture: brown, Plantation: dark green)
- Median temporal lag: ~9.4 years
- No strong correlation between distance and temporal lag

**Key Insights:**
- Spatial matching is challenging due to 10km grid spacing
- Most sites (>50%) are >30km from nearest patch
- Temporal lag dominates over spatial distance
- Land use types show similar distance/lag distributions
- Justifies accepting larger distance thresholds (20-30km)

---

## Summary Statistics

### Matching Results:
- **Total PREDICTS agricultural sites:** 15,630
- **Successfully matched:** 15,622 (99.9%)
- **Unmatched:** 8 (0.1%)

### Distance Statistics:
- **Mean:** 32.33 km
- **Median:** 30.54 km
- **Std Dev:** 15.41 km
- **Min:** 0.16 km
- **Max:** 77.77 km

### Distance Thresholds:
- **< 10 km:** 973 sites (6.2%)
- **< 20 km:** 3,507 sites (22.4%)
- **< 30 km:** 7,610 sites (48.7%)

### Temporal Statistics:
- **Mean lag:** ~9.4 years
- **Median lag:** ~9.4 years
- **Min lag:** 0.2 years (74 days)
- **Max lag:** 23.9 years (8,735 days)

### Land Use Composition:
- **Cropland:** ~60% of sites
- **Pasture:** ~30% of sites
- **Plantation forest:** ~10% of sites

---

## Generation Scripts

All figures generated using Python scripts in `viz/scripts/`:

### `generate_figure1.py`
- Loads PREDICTS and Major TOM metadata
- Creates temporal coverage timeline
- Calculates overlap statistics
- Exports publication-quality PDF + PNG

### `generate_figure2.py`
- Loads matched sites with coordinates
- Creates Robinson projection world map
- Plots sites with year-based color gradient
- Uses Cartopy for geospatial visualization
- Requires Natural Earth shapefiles (auto-downloaded)

### `generate_figure4.py`
- Loads matched sites with distances and temporal lags
- Creates 3-panel statistical analysis
- Panel A: Distance histogram with thresholds
- Panel B: Cumulative distribution curve
- Panel C: Distance vs temporal lag scatter
- Exports multi-panel figure

---

## Usage

### Regenerate Figures:
```bash
# All figures
uv run python viz/scripts/generate_figure1.py
uv run python viz/scripts/generate_figure2.py
uv run python viz/scripts/generate_figure4.py

# Or run individually as needed
```

### Dependencies:
```bash
uv add matplotlib seaborn geopandas cartopy pandas numpy
```

### File Formats:
- **PDF:** Vector format, publication-quality, scalable
- **PNG:** Raster format, 300 DPI, for preview/web

---

## Integration into Paper

### Suggested Figure Captions:

**Figure 1:**
> **Temporal coverage mismatch between PREDICTS and Major TOM datasets.** Timeline showing PREDICTS biodiversity sampling (1992-2018, n=15,630 agricultural sites) versus Major TOM satellite embeddings (2016-2024, n=2.2M patches). Color intensity represents site density per year. Overlap period (2016-2018, shaded green) contains only 216 sites (1.4%), while 15,414 sites (98.6%) fall in the temporal gap before Sentinel-2 launch (June 2015, dashed line). This mismatch necessitates a space-for-time substitution approach for biodiversity modeling.

**Figure 2:**
> **Global distribution of matched PREDICTS sites and Major TOM coverage.** World map (Robinson projection) showing 15,622 PREDICTS agricultural sites matched to nearest Major TOM satellite patches. Sites color-coded by sampling year: red (2000-2005), yellow (2006-2012), green (2013-2018). Mean matching distance: 32.3 km. Concentrations visible in tropical regions (Brazil, Central Africa, SE Asia), temperate zones (UK, Eastern Europe), and agricultural areas (North America, Australia). Land use types: Cropland (60%), Pasture (30%), Plantation forest (10%).

**Figure 4:**
> **Quantitative assessment of PREDICTS-Major TOM matching quality.** (A) Histogram of distances from PREDICTS sites to nearest Major TOM patch (mean: 32.3 km, median: 30.5 km). Dashed lines indicate distance thresholds: 10 km (973 sites, 6.2%), 20 km (3,507 sites, 22.4%), 30 km (7,610 sites, 48.7%). (B) Cumulative distribution showing percentage of sites within each distance threshold. (C) Scatter plot of distance versus temporal lag (years between biodiversity sampling and satellite observation) colored by land use type. Median temporal lag: 9.4 years. No significant correlation between spatial distance and temporal lag (r < 0.1), indicating these factors are independent.

---

## Design Specifications

### Color Palettes:
- **Temporal gradient:** Red-Yellow-Green (RdYlGn colormap)
- **Land use types:** Green shades (colorblind-friendly)
- **Thresholds:** Red (#D62828), Orange (#F77F00), Yellow (#FCBF49)
- **Main data:** Professional blue (#2E86AB, #3A7CA5)

### Typography:
- **Font family:** DejaVu Sans (publication-standard)
- **Base size:** 9-10pt
- **Titles:** 11-13pt, bold
- **Labels:** 10pt, bold
- **Annotations:** 8-9pt

### Figure Dimensions:
- **Single column:** 3.5 inches width (Nature standard)
- **Double column:** 7 inches width (used here)
- **Height:** Variable (4-9 inches depending on content)

### Export Settings:
- **Resolution:** 300 DPI
- **PDF font type:** 42 (TrueType, for editability)
- **Tight bbox:** Yes (removes excess whitespace)

---

## Notes for Paper Writing

### Key Messages to Convey:

1. **The Challenge (Figure 1):**
   - Fundamental temporal mismatch between biodiversity and satellite data
   - Limited overlap justifies space-for-time substitution
   - Demonstrates understanding of data limitations

2. **The Data (Figure 2):**
   - Global scope of analysis
   - Diverse geographic coverage strengthens generalizability
   - Successful matching of 99.9% of sites

3. **The Quality (Figure 4):**
   - Quantitative validation of matching approach
   - Distance statistics support 20-30km threshold
   - Independent spatial and temporal mismatches
   - Rigorous statistical analysis

### Addressing Potential Criticisms:

**"30km is too far for site-patch matching"**
→ Figure 4A shows this represents median performance given 10km Major TOM grid spacing. Spatial heterogeneity at this scale still captures landscape-level patterns relevant for biodiversity.

**"9-year temporal lag invalidates comparison"**
→ Figure 1 shows this is unavoidable given data availability. Space-for-time substitution is established practice in ecology, assuming land use stability (address in methods).

**"Why not use Landsat historical data?"**
→ No pre-computed embeddings available for 2000-2015 period (see data/major_tom_embedding_datasets_full_analysis.md). Generating embeddings would require weeks of computation, infeasible for demo timeline.

---

## Future Enhancements

If time permits or for final thesis:

### Additional Figures:
- **Figure 3:** Methodology flowchart (matching algorithm)
- **Figure 5:** Dataset selection rationale (radar chart comparing Major TOM options)
- **Figure 6:** Preliminary ML results (if model trained)
- **Figure S1:** Regional zooms (Europe, Brazil, SE Asia)
- **Figure S2:** Land use type specific analyses
- **Figure S3:** Temporal trend analysis by region

### Interactive Elements:
- Leaflet web map for site exploration
- Plotly dashboard for dynamic filtering
- Streamlit app for model predictions

---

## Citation

If using these visualizations in publications:

> Figures generated for PhD application to SUSTAIN CDT Project A3137 "AI for landscape ecology: tracking biodiversity impacts from land use change" using PREDICTS database (Hudson et al. 2016) and Major TOM satellite embeddings (Francis & Czerkawski 2024).

**PREDICTS:**
Hudson, L.N. et al. (2016) The database of the PREDICTS (Projecting Responses of Ecological Diversity In Changing Terrestrial Systems) project. *Ecology and Evolution*, 7(1), 145-188.

**Major TOM:**
Francis, A. & Czerkawski, M. (2024) Major TOM: Expandable Datasets for Earth Observation. *IGARSS 2024*, 2935-2940.

---

**End of README**
