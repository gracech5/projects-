# GPT Chart Generation Application 

## Introduction

This application seeks to simplify the business intelligence process by enabling the user to automatically search for a chart of interest.
Instead of having to manually click and specify their requirements, this project explores the possibility of enabling users to simplify specify in a 
search bar their chart of interest e.g. 'bar plot of COPA revenue in Europe' for example.

To explore this possibility, a fake_data.csv dataset was created in the data folder, containing randomly generated data on COPA (Revenue), avg deal size, rev yoy% etc
across different regions. Region L1 displays the data at continent level, region L2 at country level and Region L3 at the city level. 

## Deployment Steps

To deploy this application, you need to have an Open AI API Key. Create a `.env` file and set following parameters:

