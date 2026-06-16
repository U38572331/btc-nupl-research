import urllib.request
import json
import pandas as pd
import os

urls = {
    'netrealisedpnl': 'https://charts.checkonchain.com/btconchain/realised/netrealisedpnl_usd/netrealisedpnl_usd_light.html',
    'realisedpnl_ratio_lth': 'https://charts.checkonchain.com/btconchain/realised/realisedpnl_ratio_lth/realisedpnl_ratio_lth_light.html',
    'unrealised_profitloss_ratio': 'https://charts.checkonchain.com/btconchain/unrealised/unrealised_profitloss_ratio_all/unrealised_profitloss_ratio_all_light.html',
    'pricing_onchainoriginals': 'https://charts.checkonchain.com/btconchain/pricing/pricing_onchainoriginals/pricing_onchainoriginals_light.html'
}

def extract_plotly_data(url, name):
    print(f"Fetching {name}...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8')
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return
        
    start = html.find('Plotly.newPlot(')
    if start == -1:
        print(f"Plotly.newPlot not found in {name}")
        return
        
    # find the array start
    array_start = html.find('[', start)
    
    # find the matching end bracket
    count = 1
    end = array_start + 1
    in_string = False
    escape = False
    
    while count > 0 and end < len(html):
        c = html[end]
        if c == '"' and not escape:
            in_string = not in_string
            
        if c == '\\' and not escape:
            escape = True
        else:
            escape = False
            
        if not in_string:
            if c == '[': count += 1
            elif c == ']': count -= 1
            
        end += 1
        
    array_str = html[array_start:end]
    array_str = array_str.replace("NaN", "null")
    
    try:
        traces = json.loads(array_str)
        df_dict = {}
        for idx, trace in enumerate(traces):
            if 'x' in trace and 'y' in trace:
                trace_name = str(trace.get('name', f'Trace_{idx}'))
                import base64
                import numpy as np

                def parse_plotly_data(data):
                    if isinstance(data, dict):
                        if 'bdata' in data and 'dtype' in data:
                            bdata = base64.b64decode(data['bdata'])
                            dtype_map = {'float64': np.float64, 'float32': np.float32, 'int32': np.int32, 'int64': np.int64,
                                         'f8': np.float64, 'f4': np.float32, 'i4': np.int32, 'i8': np.int64}
                            dt = dtype_map.get(data['dtype'], np.float64)
                            try:
                                import zlib
                                bdata = zlib.decompress(bdata)
                            except Exception:
                                pass
                            if len(bdata) % np.dtype(dt).itemsize != 0:
                                print(f"Warning: Buffer size {len(bdata)} is not a multiple of {np.dtype(dt).itemsize} for dtype {data['dtype']}")
                                return []
                            return np.frombuffer(bdata, dtype=dt).tolist()
                        elif 'data' in data:
                            return data['data']
                        else:
                            return list(data.values())
                    return data

                dates = parse_plotly_data(trace.get('x', []))
                values = parse_plotly_data(trace.get('y', []))
                min_arr_len = min(len(dates) if isinstance(dates, list) else 0, len(values) if isinstance(values, list) else 0)
                if min_arr_len > 0 and isinstance(dates, list) and isinstance(values, list):
                    try:
                        df_trace = pd.DataFrame({'Date': dates[:min_arr_len], trace_name: values[:min_arr_len]})
                        df_trace['Date'] = pd.to_datetime(df_trace['Date'], errors='coerce')
                        df_trace.set_index('Date', inplace=True)
                        if trace_name in df_dict:
                            trace_name = f"{trace_name}_{idx}"
                        df_dict[trace_name] = df_trace
                    except Exception as e:
                        print(f"Error creating DataFrame for {trace_name}: {e}")
                    
        if df_dict:
            df_final = pd.concat(list(df_dict.values()), axis=1)
            output_file = f"{name}.csv"
            df_final.to_csv(output_file)
            print(f"Saved extracted data to {output_file}")
        else:
            print(f"No valid traces found in {name}.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error parsing JSON array for {name}: {e}")

if __name__ == "__main__":
    for name, url in urls.items():
        extract_plotly_data(url, name)
