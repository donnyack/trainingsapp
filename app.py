from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import datetime
import csv
import os

app = Flask(__name__)

# ============= Hulpfuncties =============
def oefeningen_importeren(bestandsnaam, focus):
    """Laadt oefeningen uit CSV op basis van focus (Upper/Lower)."""
    df = pd.read_csv(bestandsnaam, sep=';')
    return df.loc[df["Focus"].str.lower() == focus.lower(), "ExerciseName"].tolist()

def resultaten_opslaan(resultaten, bestandsnaam="workoutresultaten.csv"):
    """Slaat workoutresultaten op in CSV-bestand."""
    kolommen = ["Naam", "Datum", "Oefening", "Set", "Herhalingen", "Gewicht"]
    bestand_bestaat = os.path.exists(bestandsnaam)

    with open(bestandsnaam, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=kolommen)
        if not bestand_bestaat:
            writer.writeheader()
        for r in resultaten:
            writer.writerow(r)

# ============= Routes =============
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        naam = request.form['naam']
        focus = request.form['focus']
        return redirect(url_for('workout', naam=naam, focus=focus))
    return render_template('index.html')

@app.route('/workout', methods=['GET', 'POST'])
def workout():
    naam = request.args.get('naam')
    focus = request.args.get('focus')
    datum = datetime.datetime.now().strftime("%Y-%m-%d")
    oefeningen = oefeningen_importeren('exercises.csv', focus)

    if request.method == 'POST':
        resultaten = []
        for oef in oefeningen:
            sets = int(request.form.get(f'sets_{oef}', 3))
            for s in range(1, sets + 1):
                reps = request.form.get(f'reps_{oef}_{s}')
                gewicht = request.form.get(f'gewicht_{oef}_{s}')
                if reps and gewicht:
                    resultaten.append({
                        "Naam": naam,
                        "Datum": datum,
                        "Oefening": oef,
                        "Set": s,
                        "Herhalingen": int(reps),
                        "Gewicht": float(gewicht)
                    })
        resultaten_opslaan(resultaten)
        return redirect(url_for('resultaat', naam=naam, datum=datum))
    
    return render_template('workout.html', naam=naam, focus=focus, oefeningen=oefeningen)

@app.route('/resultaat')
def resultaat():
    naam = request.args.get('naam')
    datum = request.args.get('datum')
    if not os.path.exists("workoutresultaten.csv"):
        return "Geen resultaten gevonden."
    df = pd.read_csv('workoutresultaten.csv')
    sessie = df[(df['Naam'] == naam) & (df['Datum'] == datum)]
    return render_template('resultaat.html', naam=naam, datum=datum, sessie=sessie.to_dict(orient='records'))

if __name__ == "__main__":
    app.run(debug=True)
