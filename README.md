# Smart Battery for Smart Energy Usage

## Data Science for Smart Grid

The Smart Grid is the system that always tries to satisfy the equilibrium between energy supply and demand in order to maintain the operations of the system in the most efficient and safe way. This objective is achieved thanks to the two major technological advancements introduced into the grid, which make it smart:

1. The use of electronic devises (smart/digital meters) which collect data on energy demand from each user connected to the grid.
2. Analysis of obtained data with subsequent application of statistical machine learning techniques to predict future energy demand, in order to optimize production and distribution of energy.

Introduction of distributed renewable energy production (such as roof solar panels) and energy storage devices (batteries) brings new opportunities to improve the efficiency and reliability of the Smart Grid.

## Objective

One route power producing companies try to reduce their own expenses, as well as to help their consumers save on their electric bills, is the variable day tariffs on electricity (or the time-of-use tariff). The price for electricity increases during high demand hours and decreases during low demand hours, which is supposed to encourage consumers to adjust their energy usage in proportion with pricing, as it would be economically beneficial. While this approach can definitely benefit both parties, power companies and their consumers, there are obvious disadvantages to it. It is usually not easy for a typical household to change their energy consumption behavior in order to save on electric bill. Most peoples' demand is pretty typical during a day, which is high demand during mornings before leaving home for work or school, followed by low demand during the mid-day with subsequent increase of demand in evening continuing into night hours until midnight. That is where the home-based battery pack (for example, the Tesla Power-Wall) would be a great solution to this problem. Having a battery allows a household to store low-cost energy in order to use it when the price is high without altering its energy consumption behavior. I developed an algorithm which optimizes charging-standby-discharging cycles of battery pack operations in an intelligent way, so that it minimizes consumers' electric bill on a daily basis.

## Algorithm

In order to minimize daily electric bills, in the best possible way, one has to consider two sources of data:

1. Variation of energy cost within a day.
2. Local user's energy consumption behavior.

The first is assumed to be provided by the power generating company on daily basis, thus it is just a given input. The second is what has to be predicted for at least a day in advance. Once we have both, the consumer's predicted energy demand for a day and variable pricing for the same day, we can solve an optimization problem with respect to battery pack's cycles of operation to minimize the consumer's daily electrical bill. The most challenging part of the algorithm is the predictive model of the consumer's energy consumption behavior. The model should produce a forecast of the energy demand based on the energy demand of the consumer/household in the past.

There are three phases of operation of the battery pack:

1. Charging from the grid.
2. Standby.
3. Discharging to power household appliances.

The output of the algorithm is a daily schedule of these three phases. A day is split into equal time intervals, then the algorithm tells the battery which phase it should be in with each time interval.

## Data

I used a large collection of smart meter data obtained by [UK Power Networks](https://data.london.gov.uk/dataset/smartmeter-energy-use-data-in-london-households). The data contained a sample of 5,567 London households between November 2011 and February 2014. Smart meter readings of energy consumption (in kWh) were taken from half hour time intervals every day starting from 00:00 morning to 23:30 night of the same day making 48 records in one day. The data are anonymous, thus each household is given a unique household id number and Acorn group it belongs to, but no other information (such as which particular neighborhood in London the household is located in, how many rooms are in the household, or what the square footage is of each household). There is also a pricing curve of the time-of-use tariff plan in London with the following costs for electricity: high (67.20p/kWh), low (3.99p/kWh), and normal (11.76p/kWh).

The type of data is time series, below is a graph displaying a typical household with two days of energy consumption:
![MAC000035_2days_sample](https://github.com/AnatolyPavlov/smart-battery-for-smart-energy-usage/blob/master/img/fig1.png)

## The Model

The particular type of time series of households energy demand has a very distinguished daily seasonality. I have found that training a single ARMA model for this type of time series on a number of past days does not produce a good forecast for the energy demand for one day into the future. However, if I train a single ARMA model for a particular time interval in a day, let us say for 2:00pm-2:30pm, over past days, then this model gives a far better prediction for the energy demand during this time interval, ( i.e. 2:00pm-2:30pm ). This is no surprise, considering the seasonality of this time series mentioned above. It can be summarized as follows: past energy demand for a time interval in a day over a number of previous days is a better predictor of the future energy demand for the same time interval in the day than all times over previous days. This fact lead me to develop a complex model which consists of a number of ARMA sub-models. Below is outline of its architecture:

1. I split the day into a number of time intervals and trained a separate sub-model for each time interval over a number of previous days.
2. Each sub-model produces a single prediction for one day in the future, such that, all sub-models together produce a forecast for the entire day.

I also made an option to allow for training of the model for weekdays and weekends separately, which yielded better results. I developed two models, in the first model I used existing day split in the data into 48 time intervals, thus this model consists of 48 sub-models. The second model splits the day into a number of time intervals equal to the number of time intervals in the pricing curve provided by the power generating company. Then I calculate average energy demand within each of these time intervals and trained the models to predict average energy demand for each time interval for the future day. Since there are 3 time intervals in the London pricing curve, the second model consists of 3 sub-models. Below are the plots of each of the models performance for the same household. The first model is Hourly ARMA 48 sub-models and the second model is Price Correlated ARMA 3 sub-models:
![MAC000002_Model48weekdays](https://github.com/AnatolyPavlov/smart-battery-for-smart-energy-usage/blob/master/img/fig2a.png)

*Fig.1. Weekdays 48 sub-models forecast for one day. The model was trained on 350 days. The scores for this model are: MSE = 0.0108 and R^2 = 0.7405*

![MAC000002_Model3weekdays](https://github.com/AnatolyPavlov/smart-battery-for-smart-energy-usage/blob/master/img/fig5a.png)

*Fig.2. Weekdays 3 sub-models forecast for one day. The model was trained on 350 days. The scores for this model are: MSE = 0.0023 and R^2 = 0.8527*

## Optimization

The objective is to predict for each time interval how mach energy the battery pack should charge from the grid or discharge to power household appliances or standby with its current energy content. Mathematically this problem expresses as:
<p align="center"> <img src="https://github.com/AnatolyPavlov/smart-battery-for-smart-energy-usage/blob/master/equations/interval_bill.png" height="40" width="250"> </p>

<p align="center"> <img src="https://github.com/AnatolyPavlov/smart-battery-for-smart-energy-usage/blob/master/equations/min_daily_bill.png" height="75" width="170"> </p>

here in the Eq.(1) index *i* denotes a time interval in a day, thus herein all terms indexed by *i* represent values of quantities for a single time interval. The term <img src="https://github.com/AnatolyPavlov/smart-battery-for-smart-energy-usage/blob/master/equations/bi.png" height="20" width="15"> is the bill, <img src="https://github.com/AnatolyPavlov/smart-battery-for-smart-energy-usage/blob/master/equations/pi.png" height="20" width="15"> is the price per unit of energy (usually it is money value/kWh), <img src="https://github.com/AnatolyPavlov/smart-battery-for-smart-energy-usage/blob/master/equations/gi.png" height="20" width="15"> is the energy consumed from the grid due to the demand, <img src="https://github.com/AnatolyPavlov/smart-battery-for-smart-energy-usage/blob/master/equations/ci.png" height="20" width="15"> is the amount of energy the battery pack charged from the grid, and <img src="https://github.com/AnatolyPavlov/smart-battery-for-smart-energy-usage/blob/master/equations/ai.png" height="20" width="15"> is the amount of energy the battery pack discharged to power household appliances. It is assumed that battery pack can only be in a single phase within each time interval, thus <img src="https://github.com/AnatolyPavlov/smart-battery-for-smart-energy-usage/blob/master/equations/ci.png" height="20" width="15"> and <img src="https://github.com/AnatolyPavlov/smart-battery-for-smart-energy-usage/blob/master/equations/ai.png" height="20" width="15"> cannot simultaneously be not equal to zero. Equation (2) expresses minimization of the daily bill over <img src="https://github.com/AnatolyPavlov/smart-battery-for-smart-energy-usage/blob/master/equations/ci.png" height="20" width="15"> and <img src="https://github.com/AnatolyPavlov/smart-battery-for-smart-energy-usage/blob/master/equations/ai.png" height="20" width="15"> variables, here capital *N* is total number of time intervals in a day.
