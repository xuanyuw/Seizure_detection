# extract the seizure raw data from the TUSZ corpus, and save the tagged signal in each edf file into a separate csv file, 
# which contains two columns: tag: the tag of the event, signal: the raw data from the edf file.
# Tag types: aggregated category of all channel events, binary classification: seizure or not seizure.
# data source: https://www.isip.piconepress.com/projects/tuh_eeg/downloads/tuh_eeg_seizure/v1.5.1/

import pyedflib
import numpy as np
import os
import pandas as pd
from io import StringIO
def main():
    s_list = '_DOCS/05_files_with_seizures.list'
    s_files = []
    with open(s_list) as sl:
        line = sl.readline()
        while line:
            _, f = line.split('v1.5.1/')
            s_files.append(f.replace('\n', ''))
            line = sl.readline()
    home_dir = os.getcwd()
    if not os.path.exists('signal_csv'):
        os.makedirs('signal_csv')
        
    for edf in s_files:
        f = pyedflib.EdfReader(os.path.join(home_dir,edf))
        n = f.signals_in_file
        all_sf = f.getSampleFrequencies()
        
        signal_labels = f.getSignalLabels()
        sigbufs = np.zeros((n, f.getNSamples()[0]))
        print(edf)
        check_sf = np.all(all_sf == all_sf[0])
        if check_sf:
            sr = f.getSampleFrequencies()[0]
            for i in np.arange(n):
                sigbufs[i, :] = f.readSignal(i)
            folder = os.path.join(home_dir, os.path.dirname(edf))
            d = []
            for n in os.listdir(folder):
                if n.endswith('.tse_bi'):
                    with open(os.path.join(folder,n)) as lbf:
                        try: 
                            txt = lbf.read()
                            _, table = txt.split('\n\n')
                            lb = pd.read_csv(StringIO(table), sep=' ', header = None)
                        except IOError:
                            print('Couldn\'t read file %s' %n)
                            pass
                    
                    for i in range(len(lb)):
                        start = int(round(lb.iloc[i, 0]*sr))
                        end = int(round(lb.iloc[i, 1]*sr))
                        signal = sigbufs[:,start:end]
                        tag = lb.iloc[i,2]
                        d.append({'tag': tag, 'signal': signal})
            df = pd.DataFrame(d)
            name,_ = os.path.basename(edf).split('.')
            df_name = os.path.join(home_dir, 'signal_csv', name + '.csv')
            df.to_csv(df_name)
        else:
            continue
    
if __name__ == "__main__":
    main()