from enum import Enum


class Role(Enum): 
    Recruiter = "Recruiter" 
    Engineer = "Engineer"
    Designer = "Designer"
    Marketing = "Marketing"
    Accountant = "Accountant"
    ITSupport = "IT Support"
    CustomerSupport = "Customer Support"
    Founder = "Founder"


class DocumentStatus(Enum): 
    Uploading = "Uploading"
    Queued = "Queued"
    Processing = "Processing"
    Failed = "Failed"
    Completed = "Completed"
    

class SenderType(Enum): 
    LLM = "LLM"
    Client = "Client"


class OperationType(Enum): 
    GenerateDoc = "Generate Doc"


class OperationStatus(Enum): 
    Pending = "Pending"
    Done = "Done" 
    Failed = "Failed"


class IngestionJobStatus(Enum): 
    Queued = "Queued"
    Processing = "Processing"
    Completed = "Completed"
    Failed = "Failed"
    
    
class IngestionStage(Enum): 
    Pending = "Pending"
    Downloading = "Downloading"
    Chunking = "Chunking"
    Embedding = "Embedding"
    Completed = "Completed"
