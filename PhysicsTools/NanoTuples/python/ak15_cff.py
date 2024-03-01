import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import *

# ---------------------------------------------------------


def setupAK15(process, runOnMC=False, path=None, runParticleNet=False, runParticleNetMD=True):
    # recluster Puppi jets
    bTagDiscriminators = [
        'pfJetProbabilityBJetTags',
        'pfCombinedInclusiveSecondaryVertexV2BJetTags',
        'pfDeepCSVJetTags:probb',
        'pfDeepCSVJetTags:probbb',
    ]
    subjetBTagDiscriminators = [
        'pfJetProbabilityBJetTags',
        'pfCombinedInclusiveSecondaryVertexV2BJetTags',
        'pfDeepCSVJetTags:probb',
        'pfDeepCSVJetTags:probbb',
    ]
    JETCorrLevels = ['L2Relative', 'L3Absolute', 'L2L3Residual']

    from PhysicsTools.NanoTuples.jetToolbox_cff import jetToolbox
    jetToolbox(process, 'ak15', 'dummySeqAK15', 'noOutput',
               PUMethod='Puppi', JETCorrPayload='AK8PFPuppi', JETCorrLevels=JETCorrLevels,
               Cut='pt > 160.0 && abs(rapidity()) < 2.4',
               runOnMC=runOnMC,
               addNsub=True, maxTau=3,
               addSoftDrop=True, addSoftDropSubjets=True, subJETCorrPayload='AK4PFPuppi', subJETCorrLevels=JETCorrLevels,
               bTagDiscriminators=bTagDiscriminators, subjetBTagDiscriminators=subjetBTagDiscriminators)

    if runOnMC:
        process.ak15GenJetsNoNu.jetPtMin = 100
        process.ak15GenJetsNoNuSoftDrop.jetPtMin = 100

    from PhysicsTools.PatAlgos.tools.jetTools import updateJetCollection
    from RecoBTag.ONNXRuntime.pfParticleNet_cff import _pfMassDecorrelatedParticleNetJetTagsProbs as pfMassDecorrelatedParticleNetJetTagsProbs

    if runParticleNet:
        bTagDiscriminators += pfParticleNetJetTagsProbs
    if runParticleNetMD:
        bTagDiscriminators += pfMassDecorrelatedParticleNetJetTagsProbs

    updateJetCollection(
        process,
        jetSource=cms.InputTag('packedPatJetsAK15PFPuppiSoftDrop'),
        rParam=1.5,
        jetCorrections=('AK8PFPuppi', cms.vstring(JETCorrLevels), 'None'),
        btagDiscriminators=bTagDiscriminators,
        postfix='AK15ParticleNet',
    )

    # configure DeepAK15
    if runParticleNet:
        process.pfParticleNetTagInfosAK15ParticleNet.jet_radius = 1.5
        process.pfParticleNetJetTagsAK15ParticleNet.preprocess_json = 'none'
        process.pfParticleNetJetTagsAK15ParticleNet.model_path = 'none'

    if runParticleNetMD:
        process.pfParticleNetTagInfosAK15ParticleNet.jet_radius = 1.5
        process.pfMassDecorrelatedParticleNetJetTagsAK15ParticleNet.preprocess_json = 'PhysicsTools/NanoTuples/data/ParticleNet-MD/ak15/V02d/preprocess.json'
        process.pfMassDecorrelatedParticleNetJetTagsAK15ParticleNet.model_path = 'PhysicsTools/NanoTuples/data/ParticleNet-MD/ak15/V02d/particle-net.onnx'

    # src
    srcJets = cms.InputTag('selectedUpdatedPatJetsAK15ParticleNet')

    # jetID
    process.tightJetIdAK15Puppi = cms.EDProducer("PatJetIDValueMapProducer",
        filterParams=cms.PSet(
            version=cms.string('RUN2ULPUPPI'),
            quality=cms.string('TIGHT'),
        ),
        src=srcJets
    )

    process.tightJetIdLepVetoAK15Puppi = cms.EDProducer("PatJetIDValueMapProducer",
        filterParams=cms.PSet(
            version=cms.string('RUN2ULPUPPI'),
            quality=cms.string('TIGHTLEPVETO'),
        ),
        src=srcJets
    )

    process.ak15WithUserData = cms.EDProducer("PATJetUserDataEmbedder",
        src=srcJets,
        userFloats=cms.PSet(),
        userInts=cms.PSet(
            tightId=cms.InputTag("tightJetIdAK15Puppi"),
            tightIdLepVeto=cms.InputTag("tightJetIdLepVetoAK15Puppi"),
        ),
    )

    process.ak15Table = cms.EDProducer("SimpleCandidateFlatTableProducer",
        src=cms.InputTag("ak15WithUserData"),
        name=cms.string("AK15Puppi"),
        cut=cms.string(""),
        doc=cms.string("ak15 puppi jets"),
        singleton=cms.bool(False),  # the number of entries is variable
        extension=cms.bool(False),  # this is the main table for the jets
        variables=cms.PSet(P4Vars,
            jetId=Var("userInt('tightId')*2+4*userInt('tightIdLepVeto')", int, doc="Jet ID flags bit1 is loose (always false in 2017 since it does not exist), bit2 is tight, bit3 is tightLepVeto"),
            area=Var("jetArea()", float, doc="jet catchment area, for JECs", precision=10),
            rawFactor=Var("1.-jecFactor('Uncorrected')", float, doc="1 - Factor to get back to raw pT", precision=6),
            nPFConstituents=Var("numberOfDaughters()", int, doc="Number of PF candidate constituents"),
            tau1=Var("userFloat('NjettinessAK15Puppi:tau1')", float, doc="Nsubjettiness (1 axis)", precision=10),
            tau2=Var("userFloat('NjettinessAK15Puppi:tau2')", float, doc="Nsubjettiness (2 axis)", precision=10),
            tau3=Var("userFloat('NjettinessAK15Puppi:tau3')", float, doc="Nsubjettiness (3 axis)", precision=10),
            msoftdrop=Var("groomedMass()", float, doc="Corrected soft drop mass with PUPPI", precision=10),
            btagCSVV2=Var("bDiscriminator('pfCombinedInclusiveSecondaryVertexV2BJetTags')", float, doc="pfCombinedInclusiveSecondaryVertexV2 b-tag discriminator (aka CSVV2)", precision=10),
            btagDeepB=Var("bDiscriminator('pfDeepCSVJetTags:probb')+bDiscriminator('pfDeepCSVJetTags:probbb')", float, doc="DeepCSV b+bb tag discriminator", precision=10),
            btagJP=Var("bDiscriminator('pfJetProbabilityBJetTags')", float, doc="pfJetProbabilityBJetTags b-tag discriminator (aka JP)", precision=10),
            nBHadrons=Var("jetFlavourInfo().getbHadrons().size()", int, doc="number of b-hadrons"),
            nCHadrons=Var("jetFlavourInfo().getcHadrons().size()", int, doc="number of c-hadrons"),
            subJetIdx1=Var("?nSubjetCollections()>0 && subjets().size()>0?subjets()[0].key():-1", int,
                 doc="index of first subjet"),
            subJetIdx2=Var("?nSubjetCollections()>0 && subjets().size()>1?subjets()[1].key():-1", int,
                 doc="index of second subjet"),
        )
    )
    process.ak15Table.variables.pt.precision = 10

    # add nominal taggers
    if runParticleNet:
        for prob in pfParticleNetJetTagsProbs:
            name = 'ParticleNet_' + prob.split(':')[1]
            setattr(process.ak15Table.variables, name, Var("bDiscriminator('%s')" % prob, float, doc=prob, precision=-1))

    # add mass-decorelated taggers
    if runParticleNetMD:
        for prob in pfMassDecorrelatedParticleNetJetTagsProbs:
            name = 'ParticleNetMD_' + prob.split(':')[1]
            setattr(process.ak15Table.variables, name, Var("bDiscriminator('%s')" % prob, float, doc=prob, precision=-1))

    process.ak15SubJetTable = cms.EDProducer("SimpleCandidateFlatTableProducer",
        src=cms.InputTag("selectedPatJetsAK15PFPuppiSoftDropPacked", "SubJets"),
        cut=cms.string(""),
        name=cms.string("AK15PuppiSubJet"),
        doc=cms.string("ak15 puppi subjets"),
        singleton=cms.bool(False),  # the number of entries is variable
        extension=cms.bool(False),  # this is the main table for the jets
        variables=cms.PSet(P4Vars,
            area=Var("jetArea()", float, doc="jet catchment area, for JECs", precision=10),
            rawFactor=Var("1.-jecFactor('Uncorrected')", float, doc="1 - Factor to get back to raw pT", precision=6),
            btagDeepB=Var("bDiscriminator('pfDeepCSVJetTags:probb')+bDiscriminator('pfDeepCSVJetTags:probbb')", float, doc="DeepCSV b+bb tag discriminator", precision=10),
            btagCSVV2=Var("bDiscriminator('pfCombinedInclusiveSecondaryVertexV2BJetTags')", float, doc=" pfCombinedInclusiveSecondaryVertexV2 b-tag discriminator (aka CSVV2)", precision=10),
            btagJP=Var("bDiscriminator('pfJetProbabilityBJetTags')", float, doc="pfJetProbabilityBJetTags b-tag discriminator (aka JP)", precision=10),
            nBHadrons=Var("jetFlavourInfo().getbHadrons().size()", int, doc="number of b-hadrons"),
            nCHadrons=Var("jetFlavourInfo().getcHadrons().size()", int, doc="number of c-hadrons"),
        )
    )
    process.ak15SubJetTable.variables.pt.precision = 10

    process.ak15Task = cms.Task(
        process.tightJetIdAK15Puppi,
        process.tightJetIdLepVetoAK15Puppi,
        process.ak15WithUserData,
        process.ak15Table,
        process.ak15SubJetTable,
    )

    if runOnMC:
        process.genJetAK15Table = cms.EDProducer("SimpleCandidateFlatTableProducer",
            src=cms.InputTag("ak15GenJetsNoNu"),
            cut=cms.string("pt > 100."),
            name=cms.string("GenJetAK15"),
            doc=cms.string("AK15 GenJets made with visible genparticles"),
            singleton=cms.bool(False),  # the number of entries is variable
            extension=cms.bool(False),  # this is the main table for the genjets
            variables=cms.PSet(P4Vars,
            )
        )
        process.genJetAK15Table.variables.pt.precision = 10

        process.genSubJetAK15Table = cms.EDProducer("SimpleCandidateFlatTableProducer",
            src=cms.InputTag("ak15GenJetsNoNuSoftDrop", "SubJets"),
            cut=cms.string(""),
            name=cms.string("GenSubJetAK15"),
            doc=cms.string("AK15 Gen-SubJets made with visible genparticles"),
            singleton=cms.bool(False),  # the number of entries is variable
            extension=cms.bool(False),  # this is the main table for the genjets
            variables=cms.PSet(P4Vars,
            )
        )
        process.genSubJetAK15Table.variables.pt.precision = 10

        process.ak15Task.add(process.genJetAK15Table)
        process.ak15Task.add(process.genSubJetAK15Table)

        ###### hack to avoid circular dependency ######
        process.jetMC.remove(process.patJetPartons)
        process.ak15Task.add(process.patJetPartons)
        ###############################################

    if path is None:
        process.schedule.associate(process.ak15Task)
    else:
        getattr(process, path).associate(process.ak15Task)
