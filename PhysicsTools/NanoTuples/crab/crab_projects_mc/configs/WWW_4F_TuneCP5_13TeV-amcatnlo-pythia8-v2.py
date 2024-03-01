from WMCore.Configuration import Configuration
config = Configuration()
config.section_('General')
config.General.transferLogs = False
config.General.transferOutputs = True
config.General.workArea = 'crab_projects_mc'
config.General.requestName = 'WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8-v2'
config.section_('JobType')
config.JobType.numCores = 1
config.JobType.sendExternalFolder = True
config.JobType.pluginName = 'Analysis'
config.JobType.allowUndistributedCMSSW = True
config.JobType.psetName = 'mc2018_NANO.py'
config.JobType.maxMemoryMB = 2000
config.section_('Data')
config.Data.inputDataset = '/WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8/RunIISummer20UL18MiniAOD-106X_upgrade2018_realistic_v11_L1v1-v2/MINIAODSIM'
config.Data.outputDatasetTag = 'NanoTuples-v2_RunIISummer20UL18MiniAOD-106X_v11-v2'
config.Data.publication = True
config.Data.unitsPerJob = 1
config.Data.inputDBS = 'global'
config.Data.splitting = 'FileBased'
config.Data.allowNonValidInputDataset = True
config.Data.outLFNDirBase = '/store/user/qiguo/B2G/1lep/SF/Customized_NanoAOD/MC_2018/'
config.section_('Site')
config.Site.storageSite = 'T2_CN_Beijing'
config.section_('User')
config.section_('Debug')
