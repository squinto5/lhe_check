import os
import sys
import uproot
import awkward as ak
import numpy as np
import vector
vector.register_awkward()

class Processor:
    def __init__(self, input_file, mode):
        self.error = False
        self.input_file = input_file
        self.dataset = input_file.split("/")[4]
        self.mode = mode
        self.input_name = self.input_file.split("/")[-1]
        self.output_name = f"output_{self.input_name}"
        #self.copy_file()
    #def copy_file(self):
    #    try:
    #        os.system(f"xrdcp root://xrootd-cms.infn.it/{self.input_file} root://eosuser.cern.ch//eos/user/s/squinto/PTBINNEDCHECKS/")
    #    except:
    #        self.error = True
    #    if not os.path.exists(self.input_name):
    #        self.error = True
    def run_file(self):
        if self.error:
            return None
        with uproot.open(f"root://xrootd-cms.infn.it/{self.input_file}") as f:   # choose your preferred redirector
            events = f["Events"]
            pdgId = events["LHEPart_pdgId"].array()
            pt = events["LHEPart_pt"].array()
            eta = events["LHEPart_eta"].array()
            phi = events["LHEPart_phi"].array()
            mass = events["LHEPart_mass"].array()  # saving mass for additional checks
            self.weight = np.sign(events["genWeight"].array())

        if self.mode == "W":
            mask1 = ((abs(pdgId) == 11) | (abs(pdgId) == 13) | (abs(pdgId) == 15))
            mask2 = ((abs(pdgId) == 12) | (abs(pdgId) == 14) | (abs(pdgId) == 16))
        elif self.mode == "Z":
            mask1 = ((pdgId == 11) | (pdgId == 13) | (pdgId == 15) | (pdgId == 12) | (pdgId == 14) | (pdgId == 16))
            mask2 = ((pdgId == -11) | (pdgId == -13) | (pdgId == -15) | (pdgId == -12) | (pdgId == -14) | (pdgId == -16))
        elif self.mode == "Gamma":
            mask1 = (pdgId == 22)
            mask2 = None
        else:
            self.error = True

        ptl1 = vector.Array(ak.zip({"pt": pt[mask1], "eta": eta[mask1], "phi": phi[mask1], "mass": mass[mask1]}))
        if mask2 is None:
            self.final = ptl1[:,0]
        else:
            ptl2 = vector.Array(ak.zip({"pt": pt[mask2], "eta": eta[mask2], "phi": phi[mask2], "mass": mass[mask2]}))
            self.final = ptl1[:,0] + ptl2[:,0]

        if len(self.final) != len(self.weight):
            self.error = True

        if self.error:
            return None
    def save_file(self):
        with uproot.recreate(self.output_name) as f:
            f["Events"] = {
                "pt": self.final.pt,
                "mass": self.final.mass,
                "weight": self.weight
            }

        os.system(f"xrdcp {self.output_name} root://eosuser.cern.ch//eos/user/s/squinto/PTBINNEDCHECKS/{self.dataset}/{self.output_name} --force")  # change the path to the one you intend to use
        os.system(f"rm *.root")

if __name__ == "__main__":
    input_file = sys.argv[1]
    if "WtoLNu" in input_file:
        mode = "W"
    elif "DYto2L" in input_file or "Zto2Nu" in input_file:
        mode = "Z"
    else:
        mode = "Gamma"
    if input_file.endswith(".txt"):
       files = open(input_file).readlines()
       for f in files:
           f = f.strip()
           AAA = Processor(f, mode)
           AAA.run_file()
           AAA.save_file()
    else:
        AAA = Processor(input_file, mode)
        AAA.run_file()
        AAA.save_file()
