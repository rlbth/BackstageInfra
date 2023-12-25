# BackStage Deployment

This project provides is divided into 3 parts and acts as an example to deploy backstage but also to trigger a deployment of an application from backstage. There are three folders in this project 
- backstage-infra to deploy AWS infrastructure that will host backstage
- backstage-app - backstage application that is to be deployed on AWS 
- sample_app - a hello world application

For deployment of infrastructure we are using AWS CDK (Cloud Development Kit) for Infrastructure as Code.
OBS!! - Deploying these stacks to AWS will incur costs!

## Code Pipelines:
- Each stack of this project has seperate gitlab pipeline file of its own for isolated - build - test and deployment 
- Gitlab Pipeline in the main directory will build, test and deploy infrastructure, application and the sample application 


## Techstack

For this  deployment, the following labguages and libraries  are used:

- Python 3
- AWS CLI
- AWS CDK

## Documentation
Documentation for each stack is stored in its own directory for further reference.