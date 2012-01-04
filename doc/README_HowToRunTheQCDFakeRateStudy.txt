Instructions to do the data-driven QCD study on pucms7

------------------------------------------------------------------------------------------------------------------
- 0. Set up environment
------------------------------------------------------------------------------------------------------------------
cd $LQANA
cmsenv

------------------------------------------------------------------------------------------------------------------
- 1.  Run the fake rates (takes 19 minutes on pucms7):
------------------------------------------------------------------------------------------------------------------

unlink src/analysisClass.C
ln -s $LQMACRO/src2011/analysisClass_lq_QCD_FakeRateCalculation.C src/analysisClass.C
./scripts/make_rootNtupleClass.sh -f /data/LQ/ntuples/qcdskim-v3/Photon__Run2011A-May10ReReco-v1__AOD_0.root -t rootTupleTree/tree
make clean
make
./scripts/writeCommandsToRunOnMoreCutFiles_QCDFakeRateCalc_local.sh
# Do commands in : commandsToRunOnMoreCutFiles_qcdFakeRateCalc_pucms7.txt

# output .dat file: $LQDATA/enujj_analysis/QCDFakeRateCalc/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_tables.dat
# output .root file:  $LQDATA/enujj_analysis/QCDFakeRateCalc/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root

python makeLatexTable.py $LQDATA/enujj_analysis/QCDFakeRateCalc/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_tables.dat
mv table.pdf table_QCDFakeRateCalculation.pdf

python makeStackHistoTemplateV2_fromReducedSkim_QCD_FakeRateCalculation.py

python calculateFakeRate.py $LQDATA/enujj_analysis/QCDFakeRateCalc/output_cutTable_lq_QCD_FakeRateCalculation/analysisClass_lq_QCD_FakeRateCalculation_plots.root

# table pdf: table_QCDFakeRateCalculation.pdf
# plot pdfs: allPlots_QCDFakeRate_inclusive.pdf, allPlots_QCDFakeRate_1jet.pdf, allPlots_QCDFakeRate_2jet.pdf, allPlots_QCDFakeRate_3jet.pdf
# fake rate calculation pdf: fakeRate.pdf

------------------------------------------------------------------------------------------------------------------
- 2. Make sure that QCD dominates the closure test sample (takes 35m33.024s minutes on pucms7):
------------------------------------------------------------------------------------------------------------------

unlink src/analysisClass.C
ln -s $LQMACRO/src2011/analysisClass_lq_QCD_FakeRateClosureTest.C src/analysisClass.C
./scripts/make_rootNtupleClass.sh -f /data/LQ/ntuples/qcdskim-v3/Photon__Run2011A-May10ReReco-v1__AOD_0.root -t rootTupleTree/tree
make clean
make
./scripts/writeCommandsToRunOnMoreCutFiles_QCDClosureTest_ccj_DataAndMC.sh
# Do commands in commandsToRunOnMoreCutFiles_qcdClosureTest_ccj_DataAndMC_pucms7.txt

# output .dat file:  $LQDATA/eejj_analysis/QCDClosureTest_ccj_DataAndMC/output_cutTable_lq_QCD_FakeRateClosureTest_ccj_DataAndMC/analysisClass_lq_QCD_FakeRateClosureTest_tables.dat
# output .root file: $LQDATA//eejj_analysis/QCDClosureTest_ccj_DataAndMC/output_cutTable_lq_QCD_FakeRateClosureTest_ccj_DataAndMC/analysisClass_lq_QCD_FakeRateClosureTest_plots.root

python makeLatexTable.py $LQDATA/eejj_analysis/QCDClosureTest_ccj_DataAndMC/output_cutTable_lq_QCD_FakeRateClosureTest_ccj_DataAndMC/analysisClass_lq_QCD_FakeRateClosureTest_tables.dat
mv table.pdf table_QCDClosureTest_ccj_DataAndMC.pdf

python makeStackHistoTemplateV2_fromReducedSkim_QCD_FakeRateClosureTest_ccj_DataAndMC.py

# table pdf: table_QCDClosureTest_ccj_DataAndMC.pdf
# plot pdf: allPlots_QCDClosureTest_ccj_DataAndMC.pdf

------------------------------------------------------------------------------------------------------------------
- 3. Estimation using fake rates (takes 15 minutes on pucms7)
------------------------------------------------------------------------------------------------------------------

unlink src/analysisClass.C
ln -s $LQMACRO/src2011/analysisClass_lq_QCD_FakeRateClosureTest.C src/analysisClass.C
./scripts/make_rootNtupleClass.sh -f /data/LQ/ntuples/qcdskim-v3/Photon__Run2011A-May10ReReco-v1__AOD_0.root -t rootTupleTree/tree
make clean
make

./scripts/writeCommandsToRunOnMoreCutFiles_QCDClosureTest_ccj_DataOnly.sh

# Do commands in commandsToRunOnMoreCutFiles_qcdClosureTest_ccj_DataOnly_pucms7.txt

# output .dat file: $LQDATA/eejj_analysis/QCDClosureTest_ccj_DataOnly/output_cutTable_lq_QCD_FakeRateClosureTest_ccj_DataOnly/analysisClass_lq_QCD_FakeRateClosureTest_tables.dat
# output .root file: $LQDATA/eejj_analysis/QCDClosureTest_ccj_DataOnly/output_cutTable_lq_QCD_FakeRateClosureTest_ccj_DataOnly/analysisClass_lq_QCD_FakeRateClosureTest_plots.root

python makeLatexTable.py $LQDATA/eejj_analysis/QCDClosureTest_ccj_DataOnly/output_cutTable_lq_QCD_FakeRateClosureTest_ccj_DataOnly/analysisClass_lq_QCD_FakeRateClosureTest_tables.dat
mv table.pdf table_QCDClosureTest_ccj_DataOnly.pdf

python makeStackHistoTemplateV2_fromReducedSkim_QCD_FakeRateClosureTest_ccj_DataOnly.py

# table pdf: table_QCDClosureTest_ccj_DataOnly.pdf
# plots pdf: allPlots_QCDClosureTest_ccj_DataOnly.pdf

------------------------------------------------------------------------------------------------------------------
- 4. Estimation using Monte Carlo ( takes 33 minutes on pucms7 )
------------------------------------------------------------------------------------------------------------------

unlink src/analysisClass.C
ln -s $LQMACRO/src2011/analysisClass_lq_QCD_FakeRateClosureTest.C src/analysisClass.C
./scripts/make_rootNtupleClass.sh -f /data/LQ/ntuples/qcdskim-v3/Photon__Run2011A-May10ReReco-v1__AOD_0.root -t rootTupleTree/tree
make clean
make

./scripts/writeCommandsToRunOnMoreCutFiles_QCDClosureTest_ccj_DataOnly.sh

# Do commands in commandsToRunOnMoreCutFiles_qcdClosureTest_cej_DataAndMC_pucms7.txt

# output .dat file: $LQDATA:	$LQDATA//eejj_analysis/QCDClosureTest_cej_DataAndMC/output_cutTable_lq_QCD_FakeRateClosureTest_cej_DataAndMC/analysisClass_lq_QCD_FakeRateClosureTest_tables.dat
# output .root file: $LQDATA: 	$LQDATA//eejj_analysis/QCDClosureTest_cej_DataAndMC/output_cutTable_lq_QCD_FakeRateClosureTest_cej_DataAndMC/analysisClass_lq_QCD_FakeRateClosureTest_plots.root

python makeLatexTable.py  $LQDATA//eejj_analysis/QCDClosureTest_cej_DataAndMC/output_cutTable_lq_QCD_FakeRateClosureTest_cej_DataAndMC/analysisClass_lq_QCD_FakeRateClosureTest_tables.dat
mv table.pdf table_QCDClosureTest_cej_DataAndMC.pdf

python makeStackHistoTemplateV2_fromReducedSkim_QCD_FakeRateClosureTest_cej_DataAndMC.py

# table pdf: table_QCDClosureTest_cej_DataAndMC.pdf
# plots pdf: table_QCDClosureTest_cej_DataAndMC.pdf


