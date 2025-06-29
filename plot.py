import os
import uproot
import matplotlib.pyplot as plt
from multiprocessing import Pool
import numpy as np
import json

class Plotter:
    def __init__(self, sample):
        self.sample = sample
        self.PATH = f"/eos/uscms/store/group/monojet/PTBINNEDCHECKS/{sample}"
        self.bins = np.linspace(0, 1500, 31)
        self.counts = np.zeros(len(self.bins) - 1)
        self.countssq = np.zeros(len(self.bins) - 1)
        self.process()
        self.save()
    def process(self):
        for filename in os.listdir(self.PATH):
            file = f"{self.PATH}/{filename}"
            with uproot.open(file) as f:
                events = f["Events"]
                pt = events["pt"].array(library="np")
                pt = np.where(pt > 1500, 1499, pt)
                weight = events["weight"].array(library="np")
                counts, _ = np.histogram(pt, bins=self.bins, weights=weight)
                countssq, _ = np.histogram(pt, bins=self.bins, weights=weight**2)
                self.counts += counts
                self.countssq += countssq
    def save(self):
        with open("crosssection.json") as f:
            xsecs = json.load(f)
        xsec = xsecs[self.sample]
        scale = xsec/np.sum(self.counts)
        np.savez(f"{self.sample}.npz", counts=self.counts * scale, countssq = self.countssq * scale * scale, bins=self.bins)

def runPlotter(sample):
    Plotter(sample)

def main(samples):
    with Pool()as pool:
        pool.map(runPlotter, samples)

if __name__ == "__main__":
    samples = [
        "DYto2L-2Jets_Bin-1J-MLL-50-PTLL-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8",
        "DYto2L-2Jets_Bin-1J-MLL-50-PTLL-200to400_TuneCP5_13p6TeV_amcatnloFXFX-pythia8",
        "DYto2L-2Jets_Bin-1J-MLL-50-PTLL-400to600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8",
        "DYto2L-2Jets_Bin-1J-MLL-50-PTLL-600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8",
        "DYto2L-2Jets_Bin-2J-MLL-50-PTLL-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8",
        "DYto2L-2Jets_Bin-2J-MLL-50-PTLL-200to400_TuneCP5_13p6TeV_amcatnloFXFX-pythia8",
        "DYto2L-2Jets_Bin-2J-MLL-50-PTLL-400to600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8",
        "DYto2L-2Jets_Bin-2J-MLL-50-PTLL-600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8",
        "DYto2L-2Jets_MLL-50_1J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8",
        "DYto2L-2Jets_MLL-50_2J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8",
        "GJ_Bin-PTG-100to200_TuneCP5_13p6TeV_amcatnlo-pythia8",
        "GJ_Bin-PTG-130_TuneCP5_13p6TeV_amcatnlo-pythia8",
        "GJ_Bin-PTG-200to400_TuneCP5_13p6TeV_amcatnlo-pythia8",
        "GJ_Bin-PTG-30_TuneCP5_13p6TeV_amcatnlo-pythia8",
        "GJ_Bin-PTG-400to600_TuneCP5_13p6TeV_amcatnlo-pythia8",
        "GJ_Bin-PTG-600_TuneCP5_13p6TeV_amcatnlo-pythia8",
        "WtoLNu-2Jets_1J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8",
        "WtoLNu-2Jets_2J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8",
        "WtoLNu-2Jets_Bin-1J-PTLNu-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8",
        "WtoLNu-2Jets_Bin-1J-PTLNu-200to400_TuneCP5_13p6TeV_amcatnloFXFX-pythia8",
        "WtoLNu-2Jets_Bin-1J-PTLNu-400to600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8",
        "WtoLNu-2Jets_Bin-1J-PTLNu-600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8",
        "WtoLNu-2Jets_Bin-2J-PTLNu-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8",
        "WtoLNu-2Jets_Bin-2J-PTLNu-200to400_TuneCP5_13p6TeV_amcatnloFXFX-pythia8",
        "WtoLNu-2Jets_Bin-2J-PTLNu-400to600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8",
        "WtoLNu-2Jets_Bin-2J-PTLNu-600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8"
    ]
    samples = [
       "GJ_Bin-PTG-30_TuneCP5_13p6TeV_amcatnlo-pythia8",
       "GJ_Bin-PTG-130_TuneCP5_13p6TeV_amcatnlo-pythia8",
    ]
    main(samples)

