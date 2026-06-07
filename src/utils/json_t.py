import json 

def weather_json_combined(weather_data_sources):
    for i in range(len(weather_data_sources)):
        weather_data_sources[i] = json.loads(weather_data_sources[i])
    return json.dumps(weather_data_sources, ensure_ascii=False)