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

# change everywhere to the correct path
def draw_DY(gap):
    JETBINS = ["1J", "2J"]
    PTBINS = ["40to100", "100to200", "200to400", "400to600", "600"]

    DYINCL = [f"DYto2L-2Jets_MLL-50_{NJ}_TuneCP5_13p6TeV_amcatnloFXFX-pythia8" for NJ in JETBINS]
    DYPTBINNED = [f"DYto2L-2Jets_MLL-50_PTLL-{PT}_{NJ}_TuneCP5_13p6TeV_amcatnloFXFX-pythia8" for NJ in JETBINS for PT in PTBINS]
    #DYPTBINNED = [f"DYto2L-2Jets_Bin-{NJ}-MLL-50-PTLL-{PT}_TuneCP5_13p6TeV_amcatnloFXFX-pythia8" for NJ in JETBINS for PT in PTBINS]

    hists = {
        "DY Inclusive" : Stacker(f"/eos/user/s/squinto/PTBINNEDCHECKS/npzs_{gap}_XSDB", DYINCL).get(),
        "DY PT Binned" : Stacker(f"/eos/user/s/squinto/PTBINNEDCHECKS/npzs_{gap}_XSDB", DYPTBINNED).get(),
    }
    Histogrammer(hists, f"plots/npzs_{gap}_XSDB__DY").get()

def draw_Z(gap):
    JETBINS = ["1J", "2J"]
    PTBINS = ["40to100", "100to200", "200to400", "400to600", "600"]

    ZPTBINNED = [f"Zto2Nu-2Jets_Bin-PTNuNu-{PT}_TuneCP5_13p6TeV_amcatnloFXFX-pythia8" for PT in PTBINS[1:]]
    ZPTNJBINNED = [f"Zto2Nu-2Jets_PTNuNu-{PT}_{NJ}_TuneCP5_13p6TeV_amcatnloFXFX-pythia8" for NJ in JETBINS for PT in PTBINS]
    ZINCL = [f"Zto2Nu-2Jets_Bin-PTNuNu-200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8"]

    hists = {
        #"Z Inclusive" : Stacker(f"/eos/user/s/squinto/PTBINNEDCHECKS/npzs_{gap}", ZINCL).get(),
        "Z PT Binned" : Stacker(f"/eos/user/s/squinto/PTBINNEDCHECKS/npzs_{gap}", ZPTBINNED).get(),
        "Z PT NJ Binned" : Stacker(f"/eos/user/s/squinto/PTBINNEDCHECKS/npzs_{gap}", ZPTNJBINNED).get(),
    }
    Histogrammer(hists, f"npzs_{gap}_Z_Binned_ratio").get()

def draw_W(gap):
    JETBINS = ["0J", "1J", "2J"]
    PTBINS = ["40to100", "100to200", "200to400", "400to600", "600"]

    WINCL = [f"WtoLNu-2Jets_{NJ}_TuneCP5_13p6TeV_amcatnloFXFX-pythia8" for NJ in JETBINS]
    WPTBINNED = [f"WtoLNu-2Jets_PTLNu-{PT}_{NJ}_TuneCP5_13p6TeV_amcatnloFXFX-pythia8" for NJ in JETBINS[1:] for PT in PTBINS]
    WPTBINNED2 = [f"WtoLNu-2Jets_Bin-PTLNu-{PT}_TuneCP5_13p6TeV_amcatnloFXFX-pythia8" for PT in PTBINS[1:]]

    hists = {
        "W Inclusive" : Stacker(f"/eos/user/s/squinto/PTBINNEDCHECKS/npzs_{gap}", WINCL).get(),
        "W PT Binned" : Stacker(f"/eos/user/s/squinto/PTBINNEDCHECKS/npzs_{gap}", WPTBINNED).get(),
        "W PT Binned 2" : Stacker(f"/eos/user/s/squinto/PTBINNEDCHECKS/npzs_{gap}", WPTBINNED2).get(),
    }
    Histogrammer(hists, f"plots/npzs_{gap}__W").get()

def draw_Gamma(gap):
    PTBINS = ["10to100", "100to200", "200to400", "400to600", "600"]

    GINCL = ["DYGto2LG-1Jets_MLL-50_PTG-200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8"]
    GPTBINNED = [f"DYGto2LG-1Jets_MLL-50_PTG-{PT}_TuneCP5_13p6TeV_amcatnloFXFX-pythia8" for PT in PTBINS]

    hists = {
        "Gamma Inclusive" : Stacker(f"/eos/user/s/squinto/PTBINNEDCHECKS/npzs_{gap}", GINCL).get(),
        "Gamma PT Binned" : Stacker(f"/eos/user/s/squinto/PTBINNEDCHECKS/npzs_{gap}", GPTBINNED).get(),
    }
    Histogrammer(hists, f"plots/npzs_{gap}__Gamma").get()

def main():
    for gap in [10, 20, 50]:
        draw_Z(gap)
        draw_DY(gap)
        draw_W(gap)
        draw_Gamma(gap)

if __name__ == "__main__":
    main()

