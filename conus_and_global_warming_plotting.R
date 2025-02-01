### This is for creating pretty timeseries plots of the CONUS warming temperature
### vs. Global warming temperature 

# Load necessary libraries
library(ggplot2)
library(dplyr)

# Load the data
global_data <- read.csv("/Volumes/seas-mtcraig/data_sharing/Energy Burdens Under Climate Change/TGW Warming Deltas/Global Annual Deltas/Global_Annual_Delta_long_table.csv")
us_data <- read.csv("/Volumes/seas-mtcraig/data_sharing/Energy Burdens Under Climate Change/TGW Warming Deltas/CONUS_Annual_Delta.csv")

# Merge the datasets on year and scenario columns to align both global and US signals
merged_data <- merge(global_data, us_data, by = c("Year", "Weather.Scenario"), 
                     suffixes = c("_global", "_us"))

merged_data <- merged_data %>% filter(Year < 2060)

# Filter for the two scenarios
data_rcp45_hotter <- merged_data %>% filter(Weather.Scenario == "rcp45hotter")
data_rcp85_cooler <- merged_data %>% filter(Weather.Scenario == "rcp85cooler")

# Plot for rcp45_hotter scenario
plot_rcp45 <- ggplot(data_rcp45_hotter, aes(x = Global.Climate.Change..Celsius., y = CONUS.Annual.Climate.Change..Celsius.)) +
  geom_point(size = 4, color = "dodgerblue") +  # Increase point size and set color
  theme_minimal() +  # Remove gray background
  theme(aspect.ratio = 1) +  # Square the plot
  labs(title = "Global vs US Warming Signal (RCP45 Hotter Scenario)",
       x = "Global Warming Signal",
       y = "US Warming Signal")

# Plot for rcp85_cooler scenario
plot_rcp85 <- ggplot(data_rcp85_cooler, aes(x = Global.Climate.Change..Celsius., y = CONUS.Annual.Climate.Change..Celsius.)) +
  geom_point(size = 4, color = "darkorange") +  # Increase point size and set color
  theme_minimal() +  # Remove gray background
  theme(aspect.ratio = 1) +  # Square the plot
  labs(title = "Global vs US Warming Signal (RCP85 Cooler Scenario)",
       x = "Global Warming Signal",
       y = "US Warming Signal")

# Create the plot
filtered_merged_data <- filter(merged_data, Weather.Scenario %in% c("rcp45hotter", "rcp85cooler"))
plot_scenarios <- ggplot(data = filtered_merged_data, aes(x = Year, y = CONUS.Annual.Climate.Change..Celsius., color = Weather.Scenario)) +
  geom_line() +          # Add lines connecting the data points
  geom_point() +         # Add points for each data point
  labs(
    title = "Annual Climate Change in CONUS",
    x = "Year",
    y = "CONUS Annual Climate Change (°C)",
    color = "Weather Scenario"
  ) +
  theme_minimal()        # Use a clean, minimal theme

# Print the plots
print(plot_rcp45)
print(plot_rcp85)
print(plot_scenarios)

