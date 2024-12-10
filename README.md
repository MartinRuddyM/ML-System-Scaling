## ML System Scaling

### A project about testing scaling strategies for ML systems

The goal of this project is to test different ML scaling strategies for a system under heavy data flows with varying demand. This project is for the course [Advanced Topics in Software Systems](https://github.com/rdsea/sys4bigml) at Aalto University (fall 2024 edition).

## Introduction
  
In modern software systems, it’s important to design them in a way that they can handle different challenges effectively. This is where the concept of R3E comes in, which stands for Robustness, Resilience, Reliability, and Elasticity. These four factors help measure how well a system can perform under pressure, adapt to changes, and recover from issues. Among these, Elasticity is especially important when systems need to scale up or down depending on demand.

Elasticity is all about how systems use resources efficiently. For example, when there’s a spike in users or data, the system should quickly handle the extra load. At the same time, when demand drops, the system should scale down to save resources. This ability makes sure systems remain cost-effective while still performing well for users.
  
This project explores Elasticity by testing how systems can scale using different techniques. By comparing these approaches, we can gain a better understanding of what works best for creating systems that are flexible, reliable, and efficient in dynamic environments.

## Meet the ML models

In order to test the scaling strategies, we need some actual ML models taht will amke real predictions within the system. For this project, three models of different types are used. These include a simple linear regression model, a slightly more complex XGBoost model, and an image classification model. The idea is to deploy these models and have them making regular predictions. When the data flow increases over its current capacity, the system should recognize that need and scale accordingly, thus providing the opportunity to test the scalability.

1. **Linear Regression Model**  
   - **Type**: Predictive model.  
   - **Purpose**: This model predicts numerical values based on input features. For example, it could be used to predict energy consumption, temperature, or other continuous metrics depending on the dataset provided.  

2. **XGBoost Model**  
   - **Type**: Predictive model (Boosted Decision Trees).  
   - **Purpose**: XGBoost is used for making predictions based on structured data. It is particularly effective for complex datasets and is designed for regression tasks or binary/multi-class classification, depending on the problem setup.  

3. **Image Classifier Model: ResNet50**  
   - **Type**: Classification model.  
   - **Purpose**: ResNet50 is a deep learning model based on a residual neural network architecture. It classifies images into categories. For instance, it might identify whether an image contains a specific object or belongs to a certain class. It is designed to process unstructured image data and provide class probabilities as output.ResNet50 is pre-trained on large datasets like ImageNet, making it a reliable and efficient choice for image recognition and classification tasks.

Out of the three, the image classifier is of course the most resource-demanding. Therefore, the focus of data overflow has been on that model in order to create the need in the system of having to scale.


