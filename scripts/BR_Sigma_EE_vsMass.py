#!/usr/bin/env python3

from ROOT import gROOT, gStyle, gPad, TCanvas, TH2F, TGraph, kBlue, kCyan, kGreen, kYellow, kBlack, TPolyLine, TLegend
import CMS_lumi
from tdrstyle import setTDRStyle, tdrStyle
import math
import numpy
import os


def ReadXSecFile(filename):
    masses = []
    xsTh = []
    yPDF_up = []
    yPDF_down = []
    with open(os.path.expandvars(filename), "r") as xsecFile:
        for line in xsecFile:
            line = line.strip()
            if line.startswith("#"):
                continue
            split = line.split()
            if len(split) != 7:
                print("length of this line is not 7; don't know how to handle it. Quitting.  Line looks like '"+line+"'")
                exit(-1)
            masses.append(float(split[0]))
            xs = float(split[1])
            xsTh.append(xs)
            yPDF_up.append(xs*(1+float(split[5])/100.))
            yPDF_down.append(xs*(1-float(split[6])/100.))
    return masses, xsTh, yPDF_up, yPDF_down


def BR_Sigma_EE_vsMass():
    xsThFilename = "$LQANA/config/xsection_theory_13TeV_scalarPairLQ.txt"
    mTh, xsTh, y_pdf, yPDFDown = ReadXSecFile(xsThFilename)
    nTH = len(mTh)
    x_pdf = mTh
    x_pdf.extend(list(reversed(mTh)))
    y_pdf.extend(list(reversed(yPDFDown)))

    # filename for the final plot (NB: changing the name extension changes the file format)
    fileName2 = "BR_Sigma_EE.pdf"
    fileName3 = "BR_Sigma_EE.png"
    fileName1 = "BR_Sigma_EE.eps"

    # axes labels for the final plot
    title = ";M_{LQ} (GeV);#sigma #times #beta^{2} (pb)"
    # string title = ";M_{LQ} (GeV);#sigma#times2#beta(1-#beta) (pb)";

    # integrated luminosity
    lint = "35.9 fb^{-1}"
    # lint = "41.5 fb^{-1}"

    # TODO: improve limit script and have it spit out these numbers in python format
    # sep 21
    # const int massPoints=37;
    # Double_t mData[37] = {200.0 , 250.0 , 300.0 , 350.0 , 400.0 , 450.0 , 500.0 , 550.0 , 600.0 , 650.0 , 700.0 , 750.0 , 800.0 , 850.0 , 900.0 , 950.0 , 1000.0 , 1050.0 , 1100.0 , 1150.0 , 1200.0 , 1250.0 , 1300.0 , 1350.0 , 1400.0 , 1450.0 , 1500.0 , 1550.0 , 1600.0 , 1650.0 , 1700.0 , 1750.0 , 1800.0 , 1850.0 , 1900.0 , 1950.0 , 2000.0 };
    # Double_t x_shademasses[74] = {200.0 , 250.0 , 300.0 , 350.0 , 400.0 , 450.0 , 500.0 , 550.0 , 600.0 , 650.0 , 700.0 , 750.0 , 800.0 , 850.0 , 900.0 , 950.0 , 1000.0 , 1050.0 , 1100.0 , 1150.0 , 1200.0 , 1250.0 , 1300.0 , 1350.0 , 1400.0 , 1450.0 , 1500.0 , 1550.0 , 1600.0 , 1650.0 , 1700.0 , 1750.0 , 1800.0 , 1850.0 , 1900.0 , 1950.0 , 2000.0 , 2000.0 , 1950.0 , 1900.0 , 1850.0 , 1800.0 , 1750.0 , 1700.0 , 1650.0 , 1600.0 , 1550.0 , 1500.0 , 1450.0 , 1400.0 , 1350.0 , 1300.0 , 1250.0 , 1200.0 , 1150.0 , 1100.0 , 1050.0 , 1000.0 , 950.0 , 900.0 , 850.0 , 800.0 , 750.0 , 700.0 , 650.0 , 600.0 , 550.0 , 500.0 , 450.0 , 400.0 , 350.0 , 300.0 , 250.0 , 200.0 };
    # Double_t xsUp_expected[37] = {0.03636 , 0.01624 , 0.01152 , 0.007524 , 0.0052 , 0.003708 , 0.00279 , 0.0022436 , 0.0017952 , 0.0014478 , 0.0011573 , 0.0009191 , 0.00076923 , 0.00068162 , 0.00062111 , 0.000568125 , 0.000441 , 0.000361179 , 0.0003354 , 0.00029748 , 0.0002792 , 0.000267728 , 0.0002585376 , 0.0002496708 , 0.0002433618 , 0.0002374383 , 0.000234061 , 0.00023104 , 0.000229515 , 0.00022653 , 0.00022453282 , 0.00022344822 , 0.00022338371 , 0.00022098615 , 0.00021942555 , 0.0002183388 , 0.00021894323 };
    # Double_t xsUp_observed[37] = {};
    # Double_t y_1sigma[74]={0.02424 , 0.01218 , 0.00864 , 0.005434 , 0.0038 , 0.002678 , 0.0020088 , 0.00158 , 0.0012716 , 0.001026 , 0.0008165 , 0.000637 , 0.00053163 , 0.00046886 , 0.00042693 , 0.000389052 , 0.00029484 , 0.000236376 , 0.000217776 , 0.000190476 , 0.00017728 , 0.000170056 , 0.0001642086 , 0.00015861 , 0.0001545912 , 0.0001508243 , 0.0001486916 , 0.000146775 , 0.0001458028 , 0.0001449036 , 0.00014263466 , 0.00014194818 , 0.00014190473 , 0.00014038207 , 0.00013939194 , 0.000138701 , 0.00013908464 , 0.00035683145 , 0.00035584624 , 0.00035761808 , 0.00036016248 , 0.0003640681 , 0.00036417303 , 0.00036594866 , 0.000369198 , 0.0003740737 , 0.000376542 , 0.0003814826 , 0.0003870009 , 0.0003966678 , 0.0004068502 , 0.0004213926 , 0.000436392 , 0.00045504 , 0.000480186 , 0.000536016 , 0.000568449 , 0.00067851 , 0.000850824 , 0.00092435 , 0.00101061 , 0.00113157 , 0.00134225 , 0.0016756 , 0.0020748 , 0.0025619 , 0.00316 , 0.0039618 , 0.005253 , 0.0072 , 0.01045 , 0.01632 , 0.02233 , 0.04848 };
    # Double_t y_2sigma[74]={0.01818 , 0.00812 , 0.00576 , 0.00418 , 0.0028 , 0.001957 , 0.0015066 , 0.0012008 , 0.0009537 , 0.0007638 , 0.0005964 , 0.00046865 , 0.00038907 , 0.00034081 , 0.00030989 , 0.00028179 , 0.00021042 , 0.000166257 , 0.000151944 , 0.000132534 , 0.00012208 , 0.00011716 , 0.0001131102 , 0.0001092232 , 0.000106488 , 0.0001038686 , 0.0001024128 , 0.00010108 , 0.0001004146 , 9.91116e-05 , 9.823362e-05 , 9.775782e-05 , 9.773126e-05 , 9.668302e-05 , 9.599712e-05 , 9.552296e-05 , 9.578695e-05 , 0.00055716008 , 0.00055802852 , 0.00056080589 , 0.00056236219 , 0.00056846086 , 0.0005735556 , 0.00057138936 , 0.0005814612 , 0.0005840835 , 0.000593028 , 0.0005956554 , 0.0006068777 , 0.0006220368 , 0.0006353108 , 0.0006579342 , 0.000684284 , 0.00071344 , 0.000748806 , 0.000819624 , 0.000862155 , 0.00100989 , 0.001231695 , 0.00133399 , 0.00144598 , 0.00160677 , 0.00188825 , 0.0023359 , 0.0028614 , 0.0034969 , 0.0043292 , 0.0054126 , 0.007107 , 0.0098 , 0.014212 , 0.02208 , 0.03045 , 0.06666 };
    # oct. 9, 2017 data
    # const int massPoints=11;
    # Double_t mData[11] = {300.0 , 400.0 , 500.0 , 600.0 , 700.0 , 800.0 , 900.0 , 1100.0 , 1300.0 , 1400.0 , 1900.0 };
    # Double_t x_shademasses[22] = {300.0 , 400.0 , 500.0 , 600.0 , 700.0 , 800.0 , 900.0 , 1100.0 , 1300.0 , 1400.0 , 1900.0 , 1900.0 , 1400.0 , 1300.0 , 1100.0 , 900.0 , 800.0 , 700.0 , 600.0 , 500.0 , 400.0 , 300.0 };
    # Double_t xsUp_expected[11] = {0.01056 , 0.0046 , 0.002511 , 0.0014399 , 0.0009301 , 0.00066528 , 0.00047747 , 0.00038064 , 0.0003366234 , 0.0003310767 , 0.0003669419 };
    # Double_t xsUp_observed[11] = {};
    # Double_t y_1sigma[22]={0.00768 , 0.0034 , 0.0017856 , 0.0010098 , 0.0006532 , 0.00045738 , 0.00032186 , 0.000255528 , 0.000224613 , 0.0002222019 , 0.0002448126 , 0.00056586114 , 0.0005118309 , 0.0005204592 , 0.000588432 , 0.00072884 , 0.00098901 , 0.0013561 , 0.0020757 , 0.0035712 , 0.0064 , 0.0144 };
    # Double_t y_2sigma[22]={0.00576 , 0.0026 , 0.0012834 , 0.000748 , 0.0004757 , 0.00033264 , 0.00023142 , 0.000182832 , 0.0001617552 , 0.0001590435 , 0.00017630496 , 0.00084942881 , 0.0007689627 , 0.0007799274 , 0.000884208 , 0.00107331 , 0.00141669 , 0.0019099 , 0.0028611 , 0.0048546 , 0.0088 , 0.0192 };
    # LQToDEle, 2016, Oct. 21 datacard (with PDF reweight)
    # const int massPoints=27;
    # Double_t mData[27] = {300.0 , 400.0 , 500.0 , 600.0 , 700.0 , 800.0 , 900.0 , 1000.0 , 1100.0 , 1200.0 , 1300.0 , 1400.0 , 1500.0 , 1600.0 , 1700.0 , 1800.0 , 1900.0 , 2000.0 , 2100.0 , 2200.0 , 2300.0 , 2400.0 , 2600.0 , 2700.0 , 2800.0 , 2900.0 , 3000.0 };
    # Double_t x_shademasses[54] = {300.0 , 400.0 , 500.0 , 600.0 , 700.0 , 800.0 , 900.0 , 1000.0 , 1100.0 , 1200.0 , 1300.0 , 1400.0 , 1500.0 , 1600.0 , 1700.0 , 1800.0 , 1900.0 , 2000.0 , 2100.0 , 2200.0 , 2300.0 , 2400.0 , 2600.0 , 2700.0 , 2800.0 , 2900.0 , 3000.0 , 3000.0 , 2900.0 , 2800.0 , 2700.0 , 2600.0 , 2400.0 , 2300.0 , 2200.0 , 2100.0 , 2000.0 , 1900.0 , 1800.0 , 1700.0 , 1600.0 , 1500.0 , 1400.0 , 1300.0 , 1200.0 , 1100.0 , 1000.0 , 900.0 , 800.0 , 700.0 , 600.0 , 500.0 , 400.0 , 300.0 };
    # Double_t xsUp_expected[27] = {0.0100824 , 0.0043512 , 0.0024048 , 0.00151834 , 0.00096735 , 0.00068876 , 0.00057001 , 0.000401492 , 0.0003135448 , 0.0002677194 , 0.00025132645 , 0.00024633525 , 0.00024720868 , 0.00024941235 , 0.000258527788 , 0.000278207544 , 0.000291359436 , 0.00032048273 , 0.0003167868315 , 0.0003927719654 , 0.0004290224713 , 0.000466289972 , 0.000588212539 , 0.0006620760049 , 0.00072697574334 , 0.000816308903918 , 0.000899720511862 };
    # Double_t xsUp_observed[27] = {};
    # Double_t y_1sigma[54]={0.0075618 , 0.0032634 , 0.0017034 , 0.00107478 , 0.000677145 , 0.00047704 , 0.00039032 , 0.000266926 , 0.000203548 , 0.0001699998 , 0.00015967444 , 0.000157584 , 0.00015759136 , 0.000159537 , 0.000165366642 , 0.000176733288 , 0.000185086828 , 0.000203588044 , 0.00020123988 , 0.0002503731554 , 0.0002725382392 , 0.000298261634 , 0.000374956749 , 0.0004205863607 , 0.00046181415654 , 0.000518563429919 , 0.000571550961346 , 0.00146635984878 , 0.00133041596749 , 0.00118482126246 , 0.0010790480679 , 0.0009586656791 , 0.000759957036 , 0.000699218642 , 0.0006401377736 , 0.0005188231785 , 0.000522321256 , 0.000474857732 , 0.000453421776 , 0.000421350237 , 0.0004064892 , 0.00040289496 , 0.00040149375 , 0.0004096726 , 0.0004362386 , 0.0004971424 , 0.00061768 , 0.00084966 , 0.0010184 , 0.001399433 , 0.00216662 , 0.0034068 , 0.0063455 , 0.0142834 };
    # Double_t y_2sigma[54]={0.0050412 , 0.0023569 , 0.0012525 , 0.00080182 , 0.000496573 , 0.0003484 , 0.0002856 , 0.0001913705 , 0.0001420792 , 0.000117102 , 0.00010996843 , 0.00010778775 , 0.00010815748 , 0.0001091199 , 0.000113107383 , 0.000121715184 , 0.000127470096 , 0.00014021152 , 0.0001385940555 , 0.0001718377554 , 0.0001876972963 , 0.000204001876 , 0.0002573429728 , 0.0002896582509 , 0.0003180518814 , 0.000357135143063 , 0.000393627722784 , 0.00228958939767 , 0.00207732529 , 0.00184999217436 , 0.0016848368034 , 0.001496870556 , 0.001186604704 , 0.0010917671882 , 0.0009995180642 , 0.0008209305015 , 0.00081555777 , 0.00074144594 , 0.000707978736 , 0.000657901156 , 0.00063468675 , 0.00062908884 , 0.0006268815 , 0.00063960659 , 0.0006812106 , 0.0007608112 , 0.000922108 , 0.0012257 , 0.00144988 , 0.001954047 , 0.0029855 , 0.0046092 , 0.0085211 , 0.0184844 };
    # LQToDEle, 2017, Oct. 26
    massPoints = 27
    # mData = [300.0,  400.0,  500.0,  600.0,  700.0,  800.0,  900.0,  1000.0,  1100.0,  1200.0,  1300.0,  1400.0,  1500.0,  1600.0,  1700.0,  1800.0,  1900.0,  2000.0,  2100.0,  2200.0,  2300.0,  2400.0,  2500.0,  2600.0,  2700.0,  2800.0,  2900.0]
    # x_shademasses = [300.0,  400.0,  500.0,  600.0,  700.0,  800.0,  900.0,  1000.0,  1100.0,  1200.0,  1300.0,  1400.0,  1500.0,  1600.0,  1700.0,  1800.0,  1900.0,  2000.0,  2100.0,  2200.0,  2300.0,  2400.0,  2500.0,  2600.0,  2700.0,  2800.0,  2900.0,  2900.0,  2800.0,  2700.0,  2600.0,  2500.0,  2400.0,  2300.0,  2200.0,  2100.0,  2000.0,  1900.0,  1800.0,  1700.0,  1600.0,  1500.0,  1400.0,  1300.0,  1200.0,  1100.0,  1000.0,  900.0,  800.0,  700.0,  600.0,  500.0,  400.0,  300.0]
    # xsUp_expected = [0.0092422,  0.0041699,  0.0022545,  0.00131362,  0.000844819,  0.000603,  0.0004284,  0.0003226275,  0.0003281032,  0.0002976006,  0.00027586486,  0.00026360775,  0.00025691084,  0.0002483154,  0.00024450226,  0.000241316184,  0.000241151588,  0.00023744575,  0.0002335601355,  0.0002356157294,  0.0002330684763,  0.00023087383,  0.0002328733785,  0.0002292547455,  0.00023270861,  0.00023104281222,  0.000230807814072]
    # xsUp_observed = []
    # y_1sigma = [0.0067216, 0.0030821, 0.0016032, 0.00092124, 0.000593308, 0.0004154, 0.00028798, 0.000211776, 0.0002202632, 0.000198535, 0.00018519159, 0.00017584875, 0.00017139828, 0.0001656714, 0.000163625257, 0.000161980032, 0.000160889592, 0.000158417344, 0.0001558254255, 0.0001571969824, 0.0001554975299, 0.00015450189, 0.0001553673885, 0.000152953089, 0.0001552574319, 0.00015508381614, 0.000153989275053, 0.000356849165874, 0.00035813344644, 0.0003597879603, 0.0003544479733, 0.000360042771, 0.00035695129, 0.0003603443134, 0.000364282674, 0.0003611039445, 0.000367111188, 0.000372842536, 0.00037405932, 0.000378022217, 0.0003839112, 0.00039719936, 0.00040752075, 0.00042756956, 0.0004600628, 0.0005071176, 0.000506277, 0.00065212, 0.00089512, 0.001231759, 0.00189366, 0.0032064, 0.0058016, 0.012603 ]
    # y_2sigma = [0.0050412, 0.0023569, 0.0011523, 0.0006824, 0.000432083, 0.00030284, 0.00020706, 0.000150008, 0.000157716, 0.0001429452, 0.00013254936, 0.0001266405, 0.0001234374, 0.0001193013, 0.000117475603, 0.000115944744, 0.000115865952, 0.000114085454, 0.0001122179775, 0.000113205986, 0.0001119821391, 0.000110927728, 0.0001118883645, 0.0001101497368, 0.0001118092047, 0.00011100885114, 0.000110895945319, 0.000536089362951, 0.00053842309356, 0.0005391455061, 0.0005324820835, 0.0005408870265, 0.000536242764, 0.0005399791994, 0.0005458811638, 0.0005424814155, 0.000551506634, 0.000558706264, 0.000562366368, 0.000567898115, 0.0005752917, 0.00059520984, 0.0006107115, 0.00064282245, 0.0006910364, 0.0007618896, 0.000769894, 0.00095914, 0.00128104, 0.001734781, 0.00261018, 0.0043587, 0.0079772, 0.016804 ]
    # LQToDEle, 2016, 23 Mar. 2021
    mData = [300.0, 400.0, 500.0, 600.0, 700.0, 800.0, 900.0, 1000.0, 1100.0, 1200.0, 1300.0, 1400.0, 1500.0, 1600.0, 1700.0, 1800.0, 1900.0, 2000.0, 2100.0, 2200.0, 2300.0, 2400.0, 2500.0, 2600.0, 2700.0, 2800.0, 2900.0]
    x_shademasses = [300.0 , 400.0 , 500.0 , 600.0 , 700.0 , 800.0 , 900.0 , 1000.0 , 1100.0 , 1200.0 , 1300.0 , 1400.0 , 1500.0 , 1600.0 , 1700.0 , 1800.0 , 1900.0 , 2000.0 , 2100.0 , 2200.0 , 2300.0 , 2400.0 , 2500.0 , 2600.0 , 2700.0 , 2800.0 , 2900.0 , 2900.0 , 2800.0 , 2700.0 , 2600.0 , 2500.0 , 2400.0 , 2300.0 , 2200.0 , 2100.0 , 2000.0 , 1900.0 , 1800.0 , 1700.0 , 1600.0 , 1500.0 , 1400.0 , 1300.0 , 1200.0 , 1100.0 , 1000.0 , 900.0 , 800.0 , 700.0 , 600.0 , 500.0 , 400.0 , 300.0 ]
    xsUp_expected = [0.0092422 , 0.0043512 , 0.0023547 , 0.00150128 , 0.000948003 , 0.00067804 , 0.00055573 , 0.0003832925 , 0.0002970992 , 0.00024901 , 0.0002321012 , 0.00021840525 , 0.00021291724 , 0.0002071851 , 0.0002018826 , 0.00020227776 , 0.000199422004 , 0.000197805986 , 0.0001957836705 , 0.0001975973666 , 0.0001959469232 , 0.000196231652 , 0.0003485446695 , 0.0003448778521 , 0.000350320794 , 0.00034569783798 , 0.000340461455734 ]
    xsUp_observed = []
    y_1sigma = [0.0067216 , 0.0030821 , 0.0017034 , 0.00105772 , 0.000664247 , 0.00046632 , 0.00037961 , 0.000255896 , 0.0001930336 , 0.000158155 , 0.00014744019 , 0.000138768 , 0.00013526068 , 0.0001316127 , 0.000128248578 , 0.000128498328 , 0.000126684056 , 0.000125656864 , 0.0001235116215 , 0.0001255245428 , 0.0001244761487 , 0.000124656954 , 0.000221414391 , 0.0002190850083 , 0.0002225426552 , 0.00021960590718 , 0.000216279458296 , 0.000554882289608 , 0.00056341651872 , 0.0005709510194 , 0.0005620801078 , 0.000568056312 , 0.00031981737 , 0.0003193533691 , 0.0003220431156 , 0.000320647761 , 0.000322382296 , 0.0003250184 , 0.00032967132 , 0.000329027317 , 0.0003376689 , 0.00034699952 , 0.0003559605 , 0.00037828301 , 0.000405819 , 0.0004723392 , 0.000592311 , 0.00082824 , 0.00099696 , 0.001373637 , 0.0021325 , 0.0033567 , 0.0061642 , 0.0134432 ]
    y_2sigma = [0.0050412 , 0.0023569 , 0.0012525 , 0.00078476 , 0.000490124 , 0.00034036 , 0.00027846 , 0.0001825465 , 0.0001345304 , 0.0001088914 , 0.00010150932 , 9.555e-05 , 9.315252e-05 , 9.064215e-05 , 8.8320686e-05 , 8.849652e-05 , 8.7246784e-05 , 8.6540184e-05 , 8.56553925e-05 , 8.64487452e-05 , 8.57267789e-05 , 8.5851308e-05 , 0.0001524883275 , 0.0001508840668 , 0.0001532653424 , 0.00015124280622 , 0.000148951881281 , 0.00087390538722 , 0.00088734630006 , 0.0008992125838 , 0.0008852414854 , 0.0008946535995 , 0.000503692602 , 0.0005029618623 , 0.0005071980432 , 0.000507358863 , 0.000507732214 , 0.000507485704 , 0.000516982104 , 0.000518194855 , 0.000529518 , 0.00054652228 , 0.00056062125 , 0.00059059968 , 0.0006336968 , 0.0007246848 , 0.0008807455 , 0.00119476 , 0.0014204 , 0.001921802 , 0.00293432 , 0.0045591 , 0.0083398 , 0.0176442 ]

    doObserved = False

    # turn on/off batch mode
    gROOT.SetBatch(True)

    # set ROOT style
    setTDRStyle()
    gStyle.SetPadLeftMargin(0.14)
    gROOT.ForceStyle()

    c = TCanvas("c", "", 850, 800)
    c.SetBottomMargin(0.13)
    c.SetLeftMargin(0.14)
    c.SetRightMargin(0.07)
    c.SetLogy()
    c.cd()

    plotLow = 0.00001
    plotHigh = 30.

    bg = TH2F("bg", title, 800, 200., 1800., 500, plotLow, plotHigh)
    # bg = TH2F("bg", title, 900, 0., 1800., 500, plotLow, plotHigh)
    bg.GetXaxis().CenterTitle()
    bg.GetYaxis().CenterTitle()
    bg.SetStats(False)
    bg.SetTitleOffset(1., "X")
    bg.SetTitleOffset(1.25, "Y")
    bg.SetTitleSize(0.05, "X")
    bg.SetTitleSize(0.05, "Y")
    bg.SetLabelSize(0.04, "X")
    bg.SetLabelSize(0.04, "Y")
    bg.Draw()

    xsTh_vs_m = TGraph(nTH, numpy.array(mTh, dtype="f"), numpy.array(xsTh, dtype="f"))
    xsTh_vs_m.SetLineWidth(2)
    xsTh_vs_m.SetLineColor(kBlue)
    xsTh_vs_m.SetFillColor(kCyan-6)
    xsTh_vs_m.SetMarkerSize(0.00001)
    xsTh_vs_m.SetMarkerStyle(22)
    xsTh_vs_m.SetMarkerColor(kBlue)

    xsData_vs_m_expected = TGraph(massPoints, numpy.array(mData, dtype="f"), numpy.array(xsUp_expected, dtype="f"))
    xsData_vs_m_expected.SetMarkerStyle(0)
    xsData_vs_m_expected.SetMarkerColor(kBlack)
    xsData_vs_m_expected.SetLineColor(kBlack)
    xsData_vs_m_expected.SetLineWidth(2)
    xsData_vs_m_expected.SetLineStyle(7)
    xsData_vs_m_expected.SetMarkerSize(0.001)

    xsData_vs_m_observed = TGraph()
    if doObserved:
        xsData_vs_m_observed = TGraph(massPoints, mData, xsUp_observed)
        xsData_vs_m_observed.SetMarkerStyle(21)
        xsData_vs_m_observed.SetMarkerColor(kBlack)
        xsData_vs_m_observed.SetLineColor(kBlack)
        xsData_vs_m_observed.SetLineWidth(2)
        xsData_vs_m_observed.SetLineStyle(1)
        xsData_vs_m_observed.SetMarkerSize(1)

    xsUp_observed_logY = []
    xsUp_expected_logY = []
    xsTh_logY = []
    if doObserved:
        for ii in range(0, massPoints):
            xsUp_observed_logY[ii] = math.log(xsUp_observed[ii])
        xsData_vs_m_observed_log = TGraph(massPoints, numpy.array(mData, dtype="f"), numpy.array(xsUp_observed_logY, dtype="f"))
    for ii in range(0, massPoints):
        xsUp_expected_logY.append(math.log(xsUp_expected[ii]))
    for ii in range(0, nTH):
        xsTh_logY.append(math.log(xsTh[ii]))
    xsTh_vs_m_log = TGraph(nTH, numpy.array(mTh, dtype="f"), numpy.array(xsTh_logY, dtype="f"))
    xsData_vs_m_expected_log = TGraph(massPoints, numpy.array(mData, dtype="f"), numpy.array(xsUp_expected_logY, dtype="f"))

    # xsTh_vs_m_tgraph = TGraph(221, numpy.array(mTh, dtype="f"), numpy.array(xsTh, dtype="f"))

    obslim = 0.0
    exlim = 0.0
    for mtest in numpy.linspace(1200.0, 1700.0, 5000, endpoint=False):
        if pow(10.0, xsData_vs_m_expected_log.Eval(mtest))/pow(10.0, xsTh_vs_m_log.Eval(mtest)) < 1.0 and pow(10.0, xsData_vs_m_expected_log.Eval(mtest+0.1))/pow(10.0, xsTh_vs_m_log.Eval(mtest+0.10)) > 1.0:
            exlim = mtest
        if doObserved:
            if pow(10.0, xsData_vs_m_observed_log.Eval(mtest))/pow(10.0, xsTh_vs_m_log.Eval(mtest)) < 1.0 and pow(10.0, xsData_vs_m_observed_log.Eval(mtest+0.1))/pow(10.0, xsTh_vs_m_log.Eval(mtest+0.10)) > 1.0:
                obslim = mtest
    print("## LLJJ expected limit:", exlim, "GeV")
    if doObserved:
        print("## LLJJ observed limit:", obslim, "GeV")


   #  for 1-sigma and 2-sigma expected for long-lived 2D
   # exlim = 0.0
   # for (Double_t mtest=mData[0]+.10 mtest<mData[massPoints-1]-.10 mtest = mtest+0.10){
   #   if(( xsy_2sigma_2->Eval(mtest)/xsTh_vs_m_tgraph->Eval(mtest) ) < 1.0 && ( xsy_2sigma_2->Eval(mtest+0.1)/xsTh_vs_m_tgraph->Eval(mtest+0.10) ) > 1.0) exlim = mtest 
   #  }
   #  std::cout<<"## LLJJ expected limit -2 sigma: "<<exlim<<" GeV"<<std::endl

   # exlim = 0.0
   # for (Double_t mtest=mData[0]+.10 mtest<mData[massPoints-1]-.10 mtest = mtest+0.10){
   #   if(( xsy_1sigma_2->Eval(mtest)/xsTh_vs_m_tgraph->Eval(mtest) ) < 1.0 && ( xsy_1sigma_2->Eval(mtest+0.1)/xsTh_vs_m_tgraph->Eval(mtest+0.10) ) > 1.0) exlim = mtest 
   #  }
   #  std::cout<<"## LLJJ expected limit -1 sigma: "<<exlim<<" GeV"<<std::endl

   # exlim = 0.0
   # for (Double_t mtest=mData[0]+.10 mtest<mData[massPoints-1]-.10 mtest = mtest+0.10){
   #   if(( xsy_1sigma_1->Eval(mtest)/xsTh_vs_m_tgraph->Eval(mtest) ) < 1.0 && ( xsy_1sigma_1->Eval(mtest+0.1)/xsTh_vs_m_tgraph->Eval(mtest+0.10) ) > 1.0) exlim = mtest 
   #  }
   #  std::cout<<"## LLJJ expected limit +1 sigma: "<<exlim<<" GeV"<<std::endl

   # exlim = 0.0
   # for (Double_t mtest=mData[0]+.10 mtest<mData[massPoints-1]-.10 mtest = mtest+0.10){
   #   if(( xsy_2sigma_1->Eval(mtest)/xsTh_vs_m_tgraph->Eval(mtest) ) < 1.0 && ( xsy_2sigma_1->Eval(mtest+0.1)/xsTh_vs_m_tgraph->Eval(mtest+0.10) ) > 1.0) exlim = mtest 
   #  }
   #  std::cout<<"## LLJJ expected limit +2 sigma: "<<exlim<<" GeV"<<std::endl

    #  region excluded by Tevatron limits
    # x_shaded[5] = {1000,1080,1080,1000,1000}// CHANGED FOR LQ2
    x_shaded = [200, 1080, 1080, 200, 200]  # CHANGED FOR LQ2
    y_shaded = [plotLow, plotLow, plotHigh, plotHigh, plotLow]  # CHANGED FOR LQ2

    x_shaded2 = [200, 1000, 1000, 200, 200]  # CHANGED FOR LQ2
    y_shaded2 = [plotLow, plotLow, plotHigh, plotHigh, plotLow]  # CHANGED FOR LQ2

    # x_shaded3 = [840, obslim, obslim, 840, 840]  # CHANGED FOR LQ2
    x_shaded3 = [1080, obslim, obslim, 1080, 1080]  # CHANGED FOR LQ2
    y_shaded3 = [plotLow, plotLow, plotHigh, plotHigh, plotLow]  # CHANGED FOR LQ2

    p2 = TPolyLine(5, numpy.array(x_shaded2, dtype="f"), numpy.array(y_shaded2, dtype="f"), "")
    #  pl.SetFillStyle(3001)
    p2.SetFillColor(8)
    p2.SetFillStyle(3345)
    p2.SetLineColor(8)   # CHANGED FOR LQ2
    # p2.Draw()
    # p2.Draw("F")

    pl = TPolyLine(5, numpy.array(x_shaded, dtype="f"), numpy.array(y_shaded, dtype="f"), "")
    #  pl.SetFillStyle(3001)
    pl.SetLineColor(14)
    pl.SetFillColor(14)
    # pl.SetFillStyle(3344)
    pl.SetFillStyle(3354)
    # pl.Draw()
    # pl.Draw("F")

    p3 = TPolyLine(5, numpy.array(x_shaded3, dtype="f"), numpy.array(y_shaded3, dtype="f"), "")
    p3.SetLineColor(46)
    p3.SetFillColor(46)
    # p3.SetFillStyle(3354)
    p3.SetFillStyle(3345)
    # p3.Draw()
    # p3.Draw("F")

    exshade1 = TGraph(2*massPoints, numpy.array(x_shademasses, dtype="f"), numpy.array(y_1sigma, dtype="f"))
    exshade1.SetFillColor(kGreen)
    exshade2 = TGraph(2*massPoints, numpy.array(x_shademasses, dtype="f"), numpy.array(y_2sigma, dtype="f"))
    exshade2.SetFillColor(kYellow)

    exshade2.Draw("f")
    exshade1.Draw("f")

    gPad.RedrawAxis()

    grshade = TGraph(2*nTH, numpy.array(x_pdf, dtype="f"), numpy.array(y_pdf, dtype="f"))
    grshade.SetFillColor(kCyan-6)
    grshade.SetFillStyle(3001)
    grshade.Draw("f")

    xsTh_vs_m.Draw("L")
    xsData_vs_m_expected.Draw("LP")
    if doObserved:
        xsData_vs_m_observed.Draw("LP")

    grshade.SetFillStyle(1001)

    legXSize = 0.48
    legYSize = 0.27
    legXStart = 0.4
    legYStart = 0.65
    legend = TLegend(legXStart, legYStart, legXStart+legXSize, legYStart+legYSize)
    legend.SetBorderSize(1)
    legend.SetFillColor(0)
    legend.SetFillStyle(1001)
    legend.SetTextSize(.036)
    legend.SetTextFont(42)
    legend.SetMargin(0.15)
    legend.SetHeader("Scalar LQ #bar{LQ} #rightarrow eejj")
    # legend.AddEntry(p2,"ATLAS exclusion (20 fb^{-1}, 8TeV)","f")
    # legend.AddEntry(pl,"CMS exclusion (19.7 fb^{-1}, 8 TeV)","f")
    # legend.AddEntry(p3,"CMS exclusion (2.7 fb^{-1}, 13 TeV)","f")

    legend.AddEntry(xsTh_vs_m, "#sigma_{theory}#times #beta^{2}  with unc. ( #beta=1)", "lf")
    # legend.AddEntry(xsTh_vs_m,"#sigma_{theory}#times#beta^{2}  with unc. (#beta=0.5)","lf")
    # legend.AddEntry(xsTh_vs_m,"#sigma_{theory}#times2#beta(1-#beta)  with unc. (#beta=0.5)","lf")
    legend.AddEntry(xsData_vs_m_expected,  "Expected 95% CL upper limit", "lp")
    if doObserved:
        legend.AddEntry(xsData_vs_m_observed,  "Observed 95% CL upper limit", "lp")
    legend.Draw()

    c.Modified()
    c.Update()
    # draw the lumi text on the canvas
    CMS_lumi.lumi_13TeV = lint
    CMS_lumi.writeExtraText = 1
    CMS_lumi.extraText = "Preliminary"
    CMS_lumi.lumiTextSize = 0.7
    CMS_lumi.relPosX = 0.1  # control position of extraText
    CMS_lumi.hOffset = 0.0
    iPos = 0
    CMS_lumi.CMS_lumi(c, 4, iPos)

    c.SetGridx()
    c.SetGridy()
    c.RedrawAxis()
    legend.Draw()

    c.SaveAs(fileName1)
    c.SaveAs(fileName2)
    c.SaveAs(fileName3)


if __name__ == "__main__":
    BR_Sigma_EE_vsMass()
