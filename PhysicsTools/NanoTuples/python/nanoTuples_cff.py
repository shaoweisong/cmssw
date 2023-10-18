import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import Var
from PhysicsTools.NanoTuples.ak15_cff import setupAK15
from PhysicsTools.NanoTuples.ak8_cff import addParticleNetAK8, getCustomTaggerDiscriminators, addCustomTagger
from PhysicsTools.NanoTuples.pfcands_cff import addPFCands


def nanoTuples_customizeVectexTable(process):
    process.vertexTable.dlenMin = -1
    process.vertexTable.dlenSigMin = -1
    process.svCandidateTable.variables.ntracks = Var("numberOfDaughters()", int, doc="number of tracks")
    return process


def nanoTuples_customizeFatJetTable(process, runOnMC, addDeepAK8Probs=False):
    if addDeepAK8Probs:
        # add DeepAK8 raw scores: nominal
        from RecoBTag.ONNXRuntime.pfDeepBoostedJet_cff import _pfDeepBoostedJetTagsProbs
        for prob in _pfDeepBoostedJetTagsProbs:
            name = prob.split(':')[1]
            setattr(process.fatJetTable.variables, 'deepTag_' + name, Var("bDiscriminator('%s')" % prob, float, doc=prob, precision=-1))

        # add DeepAK8 raw scores: mass decorrelated
        from RecoBTag.ONNXRuntime.pfDeepBoostedJet_cff import _pfMassDecorrelatedDeepBoostedJetTagsProbs
        for prob in _pfMassDecorrelatedDeepBoostedJetTagsProbs:
            name = prob.split(':')[1]
            setattr(process.fatJetTable.variables, 'deepTagMD_' + name, Var("bDiscriminator('%s')" % prob, float, doc=prob, precision=-1))

    if runOnMC:
        process.finalGenParticles.select.append('keep+ (abs(pdgId) == 6 || abs(pdgId) == 23 || abs(pdgId) == 24 || abs(pdgId) == 25)')

    return process


def nanoTuples_addDeepAK8RawScore(process, addDeepAK8Probs=False):
    if addDeepAK8Probs:
        # add DeepAK8 raw scores: nominal
        from RecoBTag.ONNXRuntime.pfDeepBoostedJet_cff import _pfDeepBoostedJetTagsProbs
        for prob in _pfDeepBoostedJetTagsProbs:
            name = prob.split(':')[1]
            setattr(process.fatJetTable.variables, 'deepTag_' + name, Var("bDiscriminator('%s')" % prob, float, doc=prob, precision=-1))

        # add DeepAK8 raw scores: mass decorrelated
        from RecoBTag.ONNXRuntime.pfDeepBoostedJet_cff import _pfMassDecorrelatedDeepBoostedJetTagsProbs
        for prob in _pfMassDecorrelatedDeepBoostedJetTagsProbs:
            name = prob.split(':')[1]
            setattr(process.fatJetTable.variables, 'deepTagMD_' + name, Var("bDiscriminator('%s')" % prob, float, doc=prob, precision=-1))

    return process

def nanoTuples_addParticleNetRawScore(process, addParticleNetProbs=False):
    if addParticleNetProbs:
        # add ParticleNet raw scores: nominal
        from RecoBTag.ONNXRuntime.pfParticleNet_cff import _pfParticleNetJetTagsProbs
        for prob in _pfParticleNetJetTagsProbs:
            name = prob.split(':')[1]
            setattr(process.fatJetTable.variables, 'ParticleNetraw_' + name, Var("bDiscriminator('%s')" % prob, float, doc=prob, precision=-1))

        # add ParticleNet raw scores: mass decorrelated
        from RecoBTag.ONNXRuntime.pfParticleNet_cff import _pfMassDecorrelatedParticleNetJetTagsProbs
        for prob in _pfMassDecorrelatedParticleNetJetTagsProbs:
            name = prob.split(':')[1]
            setattr(process.fatJetTable.variables, 'ParticleNetMDraw_' + name, Var("bDiscriminator('%s')" % prob, float, doc=prob, precision=-1))

    return process

def nanoTuples_customizeCommon(process, runOnMC, addAK15=True, addAK8=False, addPFcands=False,  AddDeepAK8RawScore=True, addParticleNetRawScore=True, customTaggers=[]):
    pfcand_params = {'srcs': [], 'isPuppiJets':[], 'jetTables':[]}
    if addAK15:
        setupAK15(process, runOnMC=runOnMC, runParticleNet=False, runParticleNetMD=True)
        pfcand_params['srcs'].append('ak15WithUserData')
        pfcand_params['isPuppiJets'].append(True)
        pfcand_params['jetTables'].append('ak15Table')
    if addAK8:
        addParticleNetAK8(process, runParticleNet=False, runParticleNetMD=True)
        pfcand_params['srcs'].append('updatedJetsAK8WithUserData')
        pfcand_params['isPuppiJets'].append(True)
        pfcand_params['jetTables'].append('fatJetTable')
    tag_discs = []
    for name in customTaggers:
        tag_discs += getCustomTaggerDiscriminators(process, name)
    if len(tag_discs) > 0:
        addCustomTagger(process, tag_discs)
        pfcand_params['srcs'].append('updatedJetsAK8WithUserData')
        pfcand_params['isPuppiJets'].append(True)
        pfcand_params['jetTables'].append('fatJetTable')
    if addPFcands:
        addPFCands(process, outTableName='PFCands', **pfcand_params)

    if AddDeepAK8RawScore:
        nanoTuples_addDeepAK8RawScore(process, addDeepAK8Probs=True)
    if addParticleNetRawScore:
        nanoTuples_addParticleNetRawScore(process, addParticleNetProbs=True)
    # nanoTuples_customizeVectexTable(process)
    # nanoTuples_customizeFatJetTable(process, runOnMC=runOnMC)

    return process


def nanoTuples_customizeData(process):
    process = nanoTuples_customizeCommon(process, False, addAK15=False, addAK8=False, addPFcands=False, AddDeepAK8RawScore=True, addParticleNetRawScore=True, customTaggers=['DeepHWWV1', 'InclParticleTransformerV1'])

    process.NANOAODoutput.fakeNameForCrab = cms.untracked.bool(True)  # hack for crab publication
    process.add_(cms.Service("InitRootHandlers", EnableIMT=cms.untracked.bool(False)))
    return process


def nanoTuples_customizeMC(process):
    process = nanoTuples_customizeCommon(process, True, addAK15=True, addAK8=False, addPFcands=False, AddDeepAK8RawScore=True, addParticleNetRawScore=True, customTaggers=['DeepHWWV1', 'InclParticleTransformerV1'])

    process.NANOAODSIMoutput.fakeNameForCrab = cms.untracked.bool(True)  # hack for crab publication
    process.add_(cms.Service("InitRootHandlers", EnableIMT=cms.untracked.bool(False)))
    return process
