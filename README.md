# Smart Battery for Smart Energy Usage

# Data Science for Smart Grid

The Smart Grid is the system that always tries to satisfy the equilibrium between energy supply and demand in order to keep the correct operations and safety of the system. This objective is achieved thanks to two major factors: 1) The use of electronic devises (digital meters) which collect data about energy consumption, and 2) analysis of obtained data and use of machine learning techniques to derive predictions on energy usage in order to optimize production and distribution of energy in more efficient way. Introduction of distributed renewable energy production (roof solar panels) and energy storage devices (batteries) brings new opportunities for a more efficient and reliable Smart Grid.

# Objective

The technical challenge I want to solve, is to develop a predicative model of the best, in terms of cost-efficiency, operation of household battery packs (For example, the Tesla Power-wall) based on two sources of data: 1) variation of energy cost due to variation in demand, and 2) local user's energy consumption behavior. The predicative model should be flexible in a sense that it can be re-trained as more data become available from both sources in order to predict more precisely the phases of battery pack operation. It also can be further improved to include local energy production units such as roof solar panels or wind turbines. There are three phases of operation the battery pack will be considerate: 1) charging from the grid, 2) discharging to the grid, and 3) discharging to power household appliances. The forth phase should be added to account for local energy production, which would be: 4) charging from local renewable  energy producing units.

# Data

See 'data/README.txt' for information about data set used in this project.
