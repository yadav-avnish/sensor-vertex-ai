from kfp.v2.dsl import (Artifact,
                        Dataset,
                        Input,
                        Model,
                        Output,
                        Metrics,
                        ClassificationMetrics,
                        component, 
                        OutputPath, 
                        InputPath,)


import google.cloud.aiplatform as aip
from kfp import dsl
from kfp.v2 import compiler
from kfp.v2.dsl import component
from kfp.v2 import compiler

PROJECT_ID = "project-neuron-368805"
BUCKET_URI= "gs://char-rnn-classification/pipeline"


#Initialize the Vertex AI SDK for Python for your project and corresponding bucket.
aip.init(project=PROJECT_ID, staging_bucket=BUCKET_URI)


from sensor.entity.config_entity import TrainingPipelineConfig,DataIngestionConfig,DataValidationConfig,DataTransformationConfig
from sensor.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact,DataTransformationArtifact
from sensor.entity.artifact_entity import ModelEvaluationArtifact,ModelPusherArtifact,ModelTrainerArtifact
from sensor.entity.config_entity import ModelPusherConfig,ModelEvaluationConfig,ModelTrainerConfig
from sensor.exception import SensorException
import sys,os
from sensor.logger import logging
from sensor.components.data_ingestion import DataIngestion
from sensor.components.data_validation import DataValidation
from sensor.components.data_transformation import DataTransformation
from sensor.components.model_trainer import ModelTrainer
from sensor.components.model_evaluation import ModelEvaluation
from sensor.components.model_pusher import ModelPusher
from sensor.cloud_storage.s3_syncer import S3Sync
from sensor.constant.s3_bucket import TRAINING_BUCKET_NAME
from sensor.constant.training_pipeline import SAVED_MODEL_DIR


@component()
def data_ingestion(ingestion_artifact:Output[Dataset],train_file_path:Output[Artifact],test_file_path:Output[Artifact]):
    import os

    os.environ["MONGO_DB_URL"]="mongodb+srv://avnish:Aa327030@ineuron-ai-projects.7eh1w4s.mongodb.net/?retryWrites=true&w=majority"
    
    from sensor.entity.config_entity import TrainingPipelineConfig,DataIngestionConfig
    from sensor.components.data_ingestion import DataIngestion
    from sensor.constant.training_pipeline import ARTIFACT_DIR
    training_pipeline_config = TrainingPipelineConfig()
    training_pipeline_config.artifact_dir = os.path.join(ingestion_artifact.path,ARTIFACT_DIR)
    data_ingestion_config = DataIngestionConfig(training_pipeline_config=training_pipeline_config)
    data_ingestion = DataIngestion(data_ingestion_config=data_ingestion_config)
    data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
    train_file_path.path =  data_ingestion_artifact.trained_file_path
    test_file_path.path =  data_ingestion_artifact.test_file_path

    


@component()
def data_validation(validation_artifact:Output[Artifact],
                    train_file_path:Input[Artifact],
                    test_file_path:Input[Artifact],
                    valid_train_file_path:Output[Artifact],
                    valid_test_file_path:Output[Artifact],
                    ):
    import os

    os.environ["MONGO_DB_URL"]="mongodb+srv://avnish:Aa327030@ineuron-ai-projects.7eh1w4s.mongodb.net/?retryWrites=true&w=majority"
    from sensor.entity.config_entity import TrainingPipelineConfig,DataIngestionConfig
    from sensor.components.data_ingestion import DataIngestion,DataIngestionArtifact
    from sensor.constant.training_pipeline import ARTIFACT_DIR

    #prepare data ingestion artifact
    data_ingestion_artifact = DataIngestionArtifact(trained_file_path=train_file_path.path,test_file_path=test_file_path.path)
    training_pipeline_config = TrainingPipelineConfig()
    training_pipeline_config.artifact_dir = os.path.join(validation_artifact.path,ARTIFACT_DIR)
    data_validation_config = DataValidationConfig(training_pipeline_config=training_pipeline_config)
    data_validation = DataValidation(data_ingestion_artifact=data_ingestion_artifact,
    data_validation_config = data_validation_config
    )
    data_validation_artifact = data_validation.initiate_data_validation()
    valid_test_file_path.path =  data_validation_artifact.valid_test_file_path
    valid_train_file_path.path = data_validation_artifact.valid_train_file_path

# @component()
# def data_transformation():
#     pass

# @component()
# def model_trainer():
#     pass

# @component()
# def model_evaluation():
#     pass

# @component()
# def model_pusher():
#     pass



# class TrainPipeline:
#     is_pipeline_running=False
#     def __init__(self):
#         self.training_pipeline_config = TrainingPipelineConfig()
      
        


#     def start_data_ingestion(self)->DataIngestionArtifact:
#         try:
#             self.data_ingestion_config = DataIngestionConfig(training_pipeline_config=self.training_pipeline_config)
#             logging.info("Starting data ingestion")
#             data_ingestion = DataIngestion(data_ingestion_config=self.data_ingestion_config)
#             data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
#             logging.info(f"Data ingestion completed and artifact: {data_ingestion_artifact}")
#             return data_ingestion_artifact
#         except  Exception as e:
#             raise  SensorException(e,sys)

#     def start_data_validaton(self,data_ingestion_artifact:DataIngestionArtifact)->DataValidationArtifact:
#         try:
#             data_validation_config = DataValidationConfig(training_pipeline_config=self.training_pipeline_config)
#             data_validation = DataValidation(data_ingestion_artifact=data_ingestion_artifact,
#             data_validation_config = data_validation_config
#             )
#             data_validation_artifact = data_validation.initiate_data_validation()
#             return data_validation_artifact
#         except  Exception as e:
#             raise  SensorException(e,sys)

#     def start_data_transformation(self,data_validation_artifact:DataValidationArtifact):
#         try:
#             data_transformation_config = DataTransformationConfig(training_pipeline_config=self.training_pipeline_config)
#             data_transformation = DataTransformation(data_validation_artifact=data_validation_artifact,
#             data_transformation_config=data_transformation_config
#             )
#             data_transformation_artifact =  data_transformation.initiate_data_transformation()
#             return data_transformation_artifact
#         except  Exception as e:
#             raise  SensorException(e,sys)
    
#     def start_model_trainer(self,data_transformation_artifact:DataTransformationArtifact):
#         try:
#             model_trainer_config = ModelTrainerConfig(training_pipeline_config=self.training_pipeline_config)
#             model_trainer = ModelTrainer(model_trainer_config, data_transformation_artifact)
#             model_trainer_artifact = model_trainer.initiate_model_trainer()
#             return model_trainer_artifact
#         except  Exception as e:
#             raise  SensorException(e,sys)

#     def start_model_evaluation(self,data_validation_artifact:DataValidationArtifact,
#                                  model_trainer_artifact:ModelTrainerArtifact,
#                                 ):
#         try:
#             model_eval_config = ModelEvaluationConfig(self.training_pipeline_config)
#             model_eval = ModelEvaluation(model_eval_config, data_validation_artifact, model_trainer_artifact)
#             model_eval_artifact = model_eval.initiate_model_evaluation()
#             return model_eval_artifact
#         except  Exception as e:
#             raise  SensorException(e,sys)

#     def start_model_pusher(self,model_eval_artifact:ModelEvaluationArtifact):
#         try:
#             model_pusher_config = ModelPusherConfig(training_pipeline_config=self.training_pipeline_config)
#             model_pusher = ModelPusher(model_pusher_config, model_eval_artifact)
#             model_pusher_artifact = model_pusher.initiate_model_pusher()
#             return model_pusher_artifact
#         except  Exception as e:
#             raise  SensorException(e,sys)


#     def run_pipeline(self):
#         try:
            
        

#             data_ingestion_artifact:DataIngestionArtifact = self.start_data_ingestion()
#             data_validation_artifact=self.start_data_validaton(data_ingestion_artifact=data_ingestion_artifact)
#             data_transformation_artifact = self.start_data_transformation(data_validation_artifact=data_validation_artifact)
#             model_trainer_artifact = self.start_model_trainer(data_transformation_artifact)
#             model_eval_artifact = self.start_model_evaluation(data_validation_artifact, model_trainer_artifact)
#             if not model_eval_artifact.is_model_accepted:
#                 raise Exception("Trained model is not better than the best model")
#             model_pusher_artifact = self.start_model_pusher(model_eval_artifact)
#             TrainPipeline.is_pipeline_running=False
#             self.sync_artifact_dir_to_s3()
#             self.sync_saved_model_dir_to_s3()
#         except  Exception as e:
#             self.sync_artifact_dir_to_s3()
#             TrainPipeline.is_pipeline_running=False
#             raise  SensorException(e,sys)
