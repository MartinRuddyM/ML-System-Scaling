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

## System Design

The system is designed with multiple components working together to simulate, process, and monitor data flow.

![image](https://github.com/user-attachments/assets/08152b88-06b9-4016-acb3-a8406465d7aa)

Each part plays a specific role in achieving the overall goal of evaluating the scalability of machine learning models. Every code component is located in its own Docker container, and the resource usage of each can be measured accordingly.

1. **Initial Datasets**: The project starts with datasets that represent various types of data, such as numerical features or images. These datasets form the basis for testing and evaluating the performance as they are fed into the models.

2. **Influx Simulator**: This component simulates a data stream by sending data to the system. It uses the MQTT protocol to communicate, which is commonly applied in environments like IoT systems. While it replicates a real-world data flow, the focus is on simulating the data transmission rather than implementing IoT-specific details. This setup means that this project could be applied in a scenario where IoT is utilized, like an Industry 4.0 factory, for exmaple.

3. **Main Application**: The main app serves as the central hub of the system. It receives incoming data via MQTT, determines the appropriate machine learning model for the task, and routes the data accordingly. Additionally, it monitors system metrics, such as CPU and memory usage, for each component to evaluate their resource consumption during scaling.

4. **Machine Learning Models**: The system incorporates the three different machine learning models discussed above.

5. **Monitoring and Visualization**: The system uses Prometheus to collect performance metrics from the main application, such as CPU and memory usage. These metrics are visualized in Grafana, providing an intuitive way to analyze system performance and resource utilization during various scaling scenarios.

## Simulating the Data Flow

To test the scalability of the system, we use the **Influx Simulator** to simulate a rhythmic flow of data that alternates between periods of normal traffic and heavy traffic. This up-and-down traffic pattern is essential for evaluating how the system responds to changes in demand and how effectively it can scale resources to handle varying workloads.

The simulation works in a cyclic manner over a total duration of 7 minutes:
1. **Normal Traffic Phase**: The data flow begins at a steady, moderate rate, simulating normal conditions. This phase lasts for 1 minute and establishes a baseline workload for the system.
2. **Heavy Traffic Phase**: After the initial normal phase, the simulator increases the data flow significantly, representing a spike in demand. This phase lasts for 2 minutes and pushes the system to its limits, requiring additional resources to handle the increased load.
3. **Return to Normal Traffic**: The data flow decreases back to the steady normal level for 2 minutes. This tests the system's ability to release unnecessary resources and operate efficiently during lighter workloads.
4. **Final Heavy Traffic Phase**: The simulation ends with another 2-minute period of heavy traffic, forcing the system to once again scale up resources to handle the high demand.

![image](https://github.com/user-attachments/assets/50647518-728a-4c9b-8dcf-f25d8d5336c4)

This rhythmic process is crucial for testing **elasticity**, one of the key aspects of scalability. By alternating between high and low workloads, the simulator creates conditions that mimic real-world usage patterns, where systems often need to adapt dynamically to fluctuating demands. The ability of the system to scale up and down efficiently in response to these changes is a strong indicator of its scalability and performance under variable conditions.

## Scaling Strategies

In this project, we implemented two primary scaling strategies to handle changes in workload: **vertical scaling** and **horizontal scaling**. Each approach has its own features and benefits, and both were carefully implemented to test the elasticity of the system under varying traffic conditions.

1. **Vertical Scaling**:
   Vertical scaling involves increasing or decreasing the resources allocated to a single container, such as the number of CPUs. In this project, vertical scaling adjusts the CPU limits for the image model container based on its workload. This was implemented using the `docker update` command, which modifies the CPU allocation dynamically. This strategy is straightforward to implement and avoids creating additional containers. However, it has limitations, as it depends on the maximum capacity of a single machine.

2. **Horizontal Scaling**:
   Horizontal scaling involves increasing or decreasing the number of container replicas to handle the workload. In our implementation, the system scales the `image_model` service by adding or removing replicas based on CPU usage. This is achieved by simulating the scaling process within the code and tracking the number of replicas using a global variable (`image_model_replicas`). Horizontal scaling is highly elastic and can handle larger workloads by distributing the load across multiple containers. However, it introduces additional complexity, such as managing communication and balancing the load among replicas.

Both strategies are triggered and managed by the **monitoring component** in the main app, which constantly tracks CPU usage of the `image_model` service. If the usage exceeds a predefined threshold, the system scales up, and if it drops below a lower threshold, it scales down. By implementing both strategies, we were able to evaluate their efficiency and effectiveness in adapting to fluctuating traffic patterns.

## Learnings

This project offered a good opportnity to dive into the comparison of scaling strategies. It was also a good chance to practice the setup of a ML system and how its components communicate between them.

Regarding the scaling strategies tested, only horizontal and vertical scaling were used. However, the project's framework offers the possibility to test other more complex scaling strategies, such as hybrid scaling or dynamic load balancing.

Comparing both verticla and horizontal scaling, vertical can be better for small applications or when resource needs are predictable and the hardware can handle the increase. It can be faster to allocate the resources, compared to horizontal scaling where a new machine needs to be set up. In this implementation, vertical scaling takes around 6 seconds to complete, while horizontal scaling can usually take about 10 to 15 seconds. This difference could be significative depending on the use case. Horizontal scaling can be better for large applications and high-traffic systems, since it is highly elastic and it can scale indefinitely given enough resources.

Overall, this project showed the importance of designing scalable systems that can adapt to changing demands while maintaining performance and reliability. Without any scaling strategy implemented, the system collapsed due to too much traffic. These learnings will guide future efforts in building robust, efficient, and elastic systems for machine learning and beyond.
