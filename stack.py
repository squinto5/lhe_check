import numpy as np
import json
import matplotlib.pyplot as plt
import mplhep as hep
hep.style.use("CMS")

class Stacker:
    def __init__(self, inputs, group):
        self.inputs = inputs
        self.group = group
        self.counts = None
        self.countssq = None
        self.bins = None
        self._load_groups()
    def _load_groups(self):
        for dataset in self.group:
            data = np.load(f"{self.inputs}/{dataset}.npz")
            if (self.counts is None) and (self.countssq is None) and (self.bins is None):
                self.bins = data["bins"]
                self.counts = np.zeros(len(self.bins) - 1)
                self.countssq = np.zeros(len(self.bins) - 1)
            self.counts += data["counts"]
            self.countssq += data["countssq"]
    def get(self):
        return self.counts, self.countssq, self.bins

class Histogrammer:
    def __init__(self, hists, output):
        self.output = output
        self.hists = hists
        self.labels = list(self.hists.keys())
        self.bins = None
        self._check()
        self._initialize()
    def _initialize(self):
        self.fig, (self.ax, self.axr) = plt.subplots(
            2, 1, sharex=True,
            gridspec_kw={'height_ratios': [3, 1]},
            figsize=(8, 6)
        )
        self.bins_center = 0.5 * (self.bins[:-1] + self.bins[1:])
        self.widths = np.diff(self.bins)
        self.ratios = {}
    def _check(self):
        for label in self.labels:
            _, __, bins = self.hists[label]
            if self.bins is None:
                self.bins = bins
            else:
                if not np.allclose(self.bins, bins):
                    sys.exit("Bins problem")
    def _set_color(self, label):
        with open("colors.json") as f:
            colors = json.load(f)
        return colors[label]
    def get(self):
        label_ref = self.labels[0]
        counts_ref, countssq_ref, _ = self.hists[label_ref]
        unc_ref = np.divide(np.sqrt(countssq_ref), counts_ref)
        self.ax.bar(self.bins_center, counts_ref, width=self.widths, alpha=0.2, label=label_ref, color=self._set_color(label_ref))
        for label in self.labels[1:]:
            counts, countssq, _ = self.hists[label]
            unc = np.sqrt(np.divide(np.sqrt(countssq), counts) ** 2 + unc_ref ** 2)
            self.ax.bar(self.bins_center, counts, width=self.widths, alpha=0.2, label=label, color=self._set_color(label))
            ratio = np.divide(counts, counts_ref)
            self.axr.step(self.bins, np.append(ratio, ratio[-1]), where="post", color=self._set_color(label))
            ratio_unc = np.append(ratio * unc, (ratio * unc)[-1])
            self.axr.fill_between(self.bins, 1 - ratio_unc, 1 + ratio_unc, alpha=0.4, step="post", color="gray")
            self.ratios[label] = {
                "bin_edges": self.bins.tolist(),
                "ratios": ratio.tolist()
            }
        self.ax.set_ylabel("A.U.")
        self.ax.set_yscale("log")
        self.ax.legend()
        self.axr.axhline(1, ls="--", color="black")
        self.axr.set_xlabel("PT [GeV]")
        self.axr.set_ylabel("Ratio")
        self.axr.set_ylim(0.85, 1.15)
        plt.tight_layout()
        self.fig.savefig(f"{self.output}.png")

        with open(f"{self.output}_ratio.json", "w") as f:
            json.dump(self.ratios, f, indent=4)

def draw_DY(gap):
    JETBINS = ["1J", "2J"]
    PTBINS = ["100to200", "200to400", "400to600", "600"]

    DYPTBINNED = [f"DYto2L-2Jets_Bin-{NJ}-MLL-50-PTLL-{PT}_TuneCP5_13p6TeV_amcatnloFXFX-pythia8" for NJ in JETBINS for PT in PTBINS]
    DYINCL = [f"DYto2L-2Jets_MLL-50_{NJ}_TuneCP5_13p6TeV_amcatnloFXFX-pythia8" for NJ in JETBINS]

    hists = {
        "DY PT Binned" : Stacker(f"npzs_{gap}", DYPTBINNED).get(),
        "DY Inclusive" : Stacker(f"npzs_{gap}", DYINCL).get(),
    }
    Histogrammer(hists, f"npzs_{gap}__DY").get()

def draw_W(gap):
    JETBINS = ["1J", "2J"]
    PTBINS = ["100to200", "200to400", "400to600", "600"]

    WPTBINNED = [f"WtoLNu-2Jets_Bin-{NJ}-PTLNu-{PT}_TuneCP5_13p6TeV_amcatnloFXFX-pythia8" for NJ in JETBINS for PT in PTBINS]
    WINCL = [f"WtoLNu-2Jets_{NJ}_TuneCP5_13p6TeV_amcatnloFXFX-pythia8" for NJ in JETBINS]

    hists = {
        "W PT Binned" : Stacker(f"npzs_{gap}", WPTBINNED).get(),
        "W Inclusive" : Stacker(f"npzs_{gap}", WINCL).get(),
    }
    Histogrammer(hists, f"npzs_{gap}__W").get()

def draw_Gamma(gap):
    PTBINS = ["100to200", "200to400", "400to600", "600"]

    GPTBINNED = [f"GJ_Bin-PTG-{PT}_TuneCP5_13p6TeV_amcatnlo-pythia8" for PT in PTBINS]
    #GINCL = ["GJ_Bin-PTG-130_TuneCP5_13p6TeV_amcatnlo-pythia8"]
    GINCL = ["GJ_Bin-Merged_TuneCP5_13p6TeV_amcatnlo-pythia8"]

    #GINCL2 = ["GJ_Bin-PTG-30_TuneCP5_13p6TeV_amcatnlo-pythia8"]

    hists = {
        "Gamma PT Binned" : Stacker(f"npzs_{gap}", GPTBINNED).get(),
        "Gamma Inclusive" : Stacker(f"npzs_{gap}", GINCL).get(),
    }
    Histogrammer(hists, f"npzs_{gap}__Gamma").get()

def main():
    for gap in [10, 20, 50]:
        draw_DY(gap)
        draw_W(gap)
        draw_Gamma(gap)

if __name__ == "__main__":
    main()

