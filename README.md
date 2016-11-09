# Smart Battery for Smart Energy Usage

## Data Science for Smart Grid

The Smart Grid is the system that always tries to satisfy the equilibrium between energy supply and demand in order to keep the operations of the system in the most efficient and safe way. This objective is achieved thanks to the two major technological advancements introduced into the grid which make it smart:

1. The use of electronic devises (smart/digital meters) which collect data of the energy demand from each user connected to the grid.
2. Analysis of obtained data with subsequent application of statistical machine learning techniques to predict future energy demand in order to optimize production and distribution of energy.

Introduction of distributed renewable energy production (roof solar panels for example) and energy storage devices (batteries) brings new opportunities to improve efficiency and reliability of the Smart Grid.

## Objective

One way of how power producing companies try to reduce their own expances as well as to help their users to save on electric bill is they introduce variable during day tariffs on electricity, the so called time-of-use tariff. The price for electricity increases during high demand hours and decreases during low demand hours which supposed to encourage users to adopt their local energy demand coherently with pricing as one would benefit from it economically. While this approach can definately benefit both parties, power company and its costumers, there is obvious desadvantage to it. It is usually not easy for a typical household to change their energy consomption behavior in order to save on electric bill. Most peoples' demand is pretty typical during a day, which is high demand during mornings before leaving home for work or school, followed by low demand during the mid-day with subsequent increase of demand in evening continuing into night hours until midnight. That is where home-based battery pack (for example, the Tesla Power-Wall) would be a great solution to this problem. Having a battery allows household to store low-cost energy in order to use it when the price is high without altering its energy consomption behaviour. In this project I developed an algorithm which optimizes charginng-standby-discharging cycles of battery pack operation in an intellegent way, so that it minimizes electric bill on daily basis.

## Algorithm

In order to minimize daily electric bill in the best possible way one has to consider two sources of data:

1. Variation of energy cost within day.
2. Local user's energy consumption behavior.

The first assumed to be provided by the power generating company on daily basis, thus it is just a given input. The second is what has to be predicted for at least a day in advence. Once we have both, the user's predicted energy demand for a day and variable pricing for the same day, we can solve an optimization problem with respect to battery pack's cycles of operation to minimize daily electrical bill. The most challenging part of the algorithm is the predictetive model of user's energy consomption behavior. The model should produce forecast of the energy demand based on the energy demand of the user/household in the past.

There are three phases of operation of the battery pack:

1. Charging from the grid.
2. Standby.
3. Discharging to power household appliances.

The output of the algoritm is daily schedule of these three cycles. A day is split into equal time intervals then the algorithm tells to the battery in which phase should it be at every time interval.

## Data

I used large collection of smart meter data obtained by [UK Power Networks](https://data.london.gov.uk/dataset/smartmeter-energy-use-data-in-london-households) a sample of 5,567 London households between November 2011 and February 2014. Smart meter readings of energy consumption (in kWh) were taken every half hour time intervals every day starting from 00:30 morning to 00:00 night of the same day making 48 records in one day. The data are ananomus, thus each household is given unique household id number and Acorn groupe it belongs to, but no any other information, such as which particular neighborhood in London the household is located at or how many rooms or what is squeare footage of the household.

The type of data is time series, below is the graph of the typical household two days consomption:
![MAC000035_2days_sample](https://github.com/AnatolyPavlov/smart-battery-for-smart-energy-usage/blob/master/img/fig1.png)