
library(ggplot2)
library(ggforce)
library(tidyverse)

df <- read.csv("line2-station-flows.csv")

stations = c("SS01", "SS02", "SS03", "SS04", "SS05", "SS06", "SS07", "SS08", "SS09", "SS10", 
         "SS11", "SS12", "SS13", "SS14", "SS58", "SS65", "SS15", "SS16", "SS17", "SS18", 
         "SS19", "SS20", "SS21", "SS22", "SS23", "SS24", "SS25", "SS26", "SS27", "SS28", 
         "SS29")

data <- df %>% 
  filter(start_time < 1001 & start_time > 599 & sub_on_likely_direction_rank > sub_off_likely_direction_rank) %>%
  group_by(sub_on_likely, sub_off_likely) %>%
  summarise(
    trips = sum(total)
  )

complete_links <- expand.grid(sub_on_likely = stations, sub_off_likely = stations) %>%
  filter(sub_on_likely != sub_off_likely) %>%  
  mutate(trips = 1)  

final_table <- data %>%
  full_join(complete_links, by = c("sub_on_likely", "sub_off_likely")) %>%
  mutate(trips = coalesce(trips.x, trips.y)) %>%
  select(sub_on_likely, sub_off_likely, trips)


data <- final_table %>% filter_all(all_vars(. != ""))

nodes <- data.frame(
  node = stations,
  x = seq(1, 31, by = 1) 
)

max_trips <- max(data["trips"])

data <- merge(data, nodes, by.x = "sub_on_likely", by.y = "node", all.x = TRUE)
data <- merge(data, nodes, by.x = "sub_off_likely", by.y = "node", all.x = TRUE, suffixes = c("_from", "_to"))

data$mid_x <- (data$x_from + data$x_to) / 2   
data$radius <- abs(data$x_to - data$x_from) / 2 

data$trip_weight <- data$trips / max_trips

data <- data %>%
  mutate(size = case_when(
    trips < 100 ~ 0.25,
    trips >= 100 & trips < 500 ~ 0.5,
    trips > 1000 ~ 1,
    TRUE ~ 0.75  
  ))

ggplot() +
  geom_segment(data = nodes, aes(x = min(x), xend = max(x), y = 0, yend = 0), color = "white") +
  geom_arc(
    data = data,
    aes(
      x0 = mid_x,         
      y0 = 0,   
      r = radius, 
      start = pi/2, 
      end = -pi/2, 
      alpha = trip_weight ,
      size = size
    ),
    color = "#aaffca",
    inherit.aes = FALSE
  ) +
  geom_point(data = nodes, aes(x = x, y = 0), size = 3, color = "white") +
  geom_text(data = nodes, aes(x = x, y = -0.2, label = node), size = 3, vjust = 1, color = "white") +
  scale_linewidth(range = c(1, 6)) +
  scale_size_continuous(range = c(1,8)) +
  scale_alpha_continuous(range = c(0.05,0.8)) +
  theme_void() +
  theme(legend.position = "none") +
  labs(title = "", subtitle = "") + theme(
    plot.background = element_rect(fill = "black"),  
    panel.background = element_rect(fill = "black"),
  )
