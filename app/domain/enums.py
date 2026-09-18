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


class SenderType(Enum): 
    LLM = "LLM"
    Client = "Client"


class OperationType(Enum): 
    GenerateDoc = "Generate Doc"


class OperationStatus(Enum): 
    Pending = "Pending"
    Done = "Done" 
    Failed = "Failed"
