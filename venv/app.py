from flask import Flask, jsonify
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.plugins.sparql import prepareQuery
from jnius import autoclass

# Load Jena classes
ReasonerFactory = autoclass("org.apache.jena.reasoner.ReasonerFactory")
Reasoner = autoclass("org.apache.jena.reasoner.Reasoner")
InfModel = autoclass("org.apache.jena.rdf.model.InfModel")


app = Flask(__name__)

@app.route('/test')
def test():
    # Load RDF data
    g = Graph()
    g.parse("http://localhost:3030/droneCrashWeather/data", format="turtle")

    # Define namespace
    ns1 = Namespace("http://ubt/crashedDrones#")

    # Define the rule
    rule = """
        PREFIX ns1: <http://ubt/crashedDrones#>
        CONSTRUCT {
            ?d ns1:hasRisk "High" .
        }
        WHERE {
            ?d ns1:Drone ?e .
            ?e ns1:CrashEvent ?f .
            ?d ns1:involvedInCrash ?f .
            ?f ns1:weather "Heavy Rain/Snow" .
        }
    """

    # Apply reasoning
    inferred_graph = g.query(rule)

    # Create a new graph and add inferred triples to it
    inferred_result_graph = Graph()
    for triple in inferred_graph:
        inferred_result_graph.add(triple)

    # Query the inferred model
    queryString = """
        PREFIX ns1: <http://ubt/crashedDrones#>
        SELECT ?d WHERE { ?d ns1:hasRisk "High" }
    """
    qe = inferred_result_graph.query(queryString)

    # Process the results
    drones_with_high_risk = [str(result["d"]) for result in qe]

    return jsonify({'drones_with_high_risk': drones_with_high_risk})

@app.route('/query')
def query_drone_crash_weather():
    
    g = Graph()
    g.parse("http://localhost:3030/droneCrashWeather/data", format="turtle")
    
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX onto: <http://ubt/crashedDrones#>

    SELECT ?model (COUNT(?model) AS ?crashCount) WHERE
    {   
      ?drone rdf:type onto:Drone .
      ?drone onto:involvedInCrash ?crashEvent .
      ?crashEvent onto:weather "Fog" .
      ?drone onto:model ?model .
    }
    GROUP BY ?model
    ORDER BY DESC(?crashCount)
    LIMIT 1
    """
    
    results = g.query(query)
    
    data = []
    for row in results:
        print(row) 
        data.append({
            "subject": row[0] if len(row) > 0 else None,
            "property": row[1] if len(row) > 1 else None,
            "object": row[2] if len(row) > 2 else None
        })

    return jsonify(data)


@app.route('/modelAndLocation')
def getModelAndLocation():
    
    g = Graph()
    g.parse("http://localhost:3030/droneCrashWeather/data", format="turtle")
    
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX onto: <http://ubt/crashedDrones#>

    SELECT ?model ?location WHERE
    {   
      ?drone rdf:type onto:Drone .
      ?drone onto:involvedInCrash ?crashEvent .
      ?drone onto:model ?model .
      ?crashEvent onto:location ?location .
    }
    """
    
    results = g.query(query)
    
    data = []
    for row in results:
        print(row) 
        data.append({
            "subject": row[0] if len(row) > 0 else None,
            "property": row[1] if len(row) > 1 else None,
            "object": row[2] if len(row) > 2 else None
        })

    return jsonify(data)

@app.route('/countByAllWeatherConditions')
def countByAllWeatherConditions():
    
    g = Graph()
    g.parse("http://localhost:3030/droneCrashWeather/data", format="turtle")
    
    query = """
      PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
      PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
      PREFIX onto: <http://ubt/crashedDrones#>

      SELECT ?weather (COUNT(?crashEvent) AS ?crashCount) WHERE
      {   
        ?drone rdf:type onto:Drone .
        ?drone onto:involvedInCrash ?crashEvent .
        ?crashEvent onto:location ?location .
        ?crashEvent onto:weather ?weather .
      }
      GROUP BY ?weather

    """
    
    results = g.query(query)
    
    data = []
    for row in results:
        print(row) 
        data.append({
            "subject": row[0] if len(row) > 0 else None,
            "property": row[1] if len(row) > 1 else None,
            "object": row[2] if len(row) > 2 else None
        })

    return jsonify(data)

@app.route('/countModelBySpecificWeatherCondition/<string:weather_condition>')
def getModelBySpecificWeatherCondition(weather_condition):
    
    weather_condition = weather_condition.capitalize()

    g = Graph()
    g.parse("http://localhost:3030/droneCrashWeather/data", format="turtle")
    
    query = f"""
     PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
      PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
      PREFIX onto: <http://ubt/crashedDrones#>

      SELECT ?model (COUNT(?model) AS ?crashCount) WHERE
      {{   
        ?drone rdf:type onto:Drone .
        ?drone onto:involvedInCrash ?crashEvent .
        ?crashEvent onto:weather "{weather_condition}" .
        ?drone onto:model ?model .
      }}
      GROUP BY ?model
      ORDER BY DESC(?crashCount)
      LIMIT 1
    """
    
    results = g.query(query)
    
    data = []
    for row in results:
        print(row) 
        data.append({
            "subject": row[0] if len(row) > 0 else None,
            "property": row[1] if len(row) > 1 else None,
            "object": row[2] if len(row) > 2 else None
        })

    return jsonify(data)

@app.route('/countCrashedEventsBySpecificWeatherCondition/<string:weather_condition>')
def countEventsBySpecificWeatherCondition(weather_condition):
    
    weather_condition = weather_condition.capitalize()

    g = Graph()
    g.parse("http://localhost:3030/droneCrashWeather/data", format="turtle")
    
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX onto: <http://ubt/crashedDrones#>

    SELECT (COUNT(?crashEvent) AS ?crashCount) WHERE
    {{   
        ?drone rdf:type onto:Drone .
        ?drone onto:involvedInCrash ?crashEvent .
        ?crashEvent onto:weather "{weather_condition}" .
    }}
    """
    
    results = g.query(query)
    
    data = []
    for row in results:
        print(row) 
        data.append({
            "subject": row[0] if len(row) > 0 else None,
            "property": row[1] if len(row) > 1 else None,
            "object": row[2] if len(row) > 2 else None
        })

    return jsonify(data)

@app.route('/whichModelHasMostCrashes')
def whichModelHasMostCrashes():
    
    g = Graph()
    g.parse("http://localhost:3030/droneCrashWeather/data", format="turtle")
    
    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX onto: <http://ubt/crashedDrones#>

        SELECT ?model (COUNT(?crashEvent) AS ?crashCount) WHERE
        {{   
            ?drone rdf:type onto:Drone .
            ?drone onto:involvedInCrash ?crashEvent .
            ?drone onto:model ?model .
        }}
        GROUP BY ?model
        ORDER BY DESC(COUNT(?crashEvent))
        LIMIT 1
    """
    
    results = g.query(query)
    
    data = []
    for row in results:
        print(row) 
        data.append({
            "subject": row[0] if len(row) > 0 else None,
            "property": row[1] if len(row) > 1 else None,
            "object": row[2] if len(row) > 2 else None
        })

    return jsonify(data)

@app.route('/countModelAndOperatorInvolvedInCrash')
def countModelAndOperatorInvolvedInCrash():
    
    g = Graph()
    g.parse("http://localhost:3030/droneCrashWeather/data", format="turtle")
    
    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX onto: <http://ubt/crashedDrones#>

        SELECT ?model ?operator (COUNT(*) AS ?crashCount) WHERE
        {   
        ?drone rdf:type onto:Drone .
        ?drone onto:involvedInCrash ?crashEvent .
        ?drone onto:model ?model .
        ?drone onto:operator ?operator .
        }
        GROUP BY ?model ?operator
        ORDER BY ?model
    """
    
    results = g.query(query)
    
    data = []
    for row in results:
        print(row) 
        data.append({
            "subject": row[0] if len(row) > 0 else None,
            "property": row[1] if len(row) > 1 else None,
            "object": row[2] if len(row) > 2 else None
        })

    return jsonify(data)

@app.route('/countAllCrashedByPhase')
def countAllCrashedByPhase():
    
    g = Graph()
    g.parse("http://localhost:3030/droneCrashWeather/data", format="turtle")
    
    query = """
       PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
       PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX onto: <http://ubt/crashedDrones#>

        SELECT ?phase (COUNT(?crashEvent) AS ?crashCount) WHERE
        {   
        ?crashEvent rdf:type onto:CrashEvent .
        ?crashEvent onto:phase ?phase .
        }
        GROUP BY ?phase
    """
    
    results = g.query(query)
    
    data = []
    for row in results:
        print(row) 
        data.append({
            "subject": row[0] if len(row) > 0 else None,
            "property": row[1] if len(row) > 1 else None,
            "object": row[2] if len(row) > 2 else None
        })

    return jsonify(data)

@app.route('/phaseWithMostCrashedEvents')
def phaseWithMostCrashedEvents():
    
    g = Graph()
    g.parse("http://localhost:3030/droneCrashWeather/data", format="turtle")
    
    query = """
       PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX onto: <http://ubt/crashedDrones#>

        SELECT ?phase (COUNT(?crashEvent) AS ?crashCount) WHERE
        {   
        ?crashEvent rdf:type onto:CrashEvent .
        ?crashEvent onto:phase ?phase .
        }
        GROUP BY ?phase
        ORDER BY DESC(?crashCount)
        LIMIT 1
    """
    
    results = g.query(query)
    
    data = []
    for row in results:
        print(row) 
        data.append({
            "subject": row[0] if len(row) > 0 else None,
            "property": row[1] if len(row) > 1 else None,
            "object": row[2] if len(row) > 2 else None
        })

    return jsonify(data)

@app.route('/getAllData')
def getAllData():
    
    g = Graph()

    # Assuming you're loading RDF data from a specific URL
    g.parse("http://localhost:3030/droneCrashWeather/data", format="turtle")
    
    query = """
       PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX onto: <http://ubt/crashedDrones#>

        SELECT ?model ?operator ?date ?location ?phase ?weather
        WHERE {
        ?drone rdf:type onto:Drone .
        ?drone onto:model ?model .
        ?drone onto:operator ?operator .
        OPTIONAL {
            ?drone onto:involvedInCrash ?crashEvent .
            ?crashEvent onto:date ?date .
            ?crashEvent onto:location ?location .
            ?crashEvent onto:phase ?phase .
            ?crashEvent onto:weather ?weather .
        }
        }
        ORDER BY ?drone
    """
    
    results = g.query(query)
    
    data = []
    for row in results:
        row_dict = {}
        for var in results.vars:
            val = row[var]
            row_dict[str(var)] = str(val) if val else None
        data.append(row_dict)

    return jsonify(data)

@app.route('/filterDataByPhase/<string:phase>')
def filterDataByPhase(phase):
    phase = phase.capitalize()

    g = Graph()
    g.parse("http://localhost:3030/droneCrashWeather/data", format="turtle")
    
    query = f"""
       PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX onto: <http://ubt/crashedDrones#>

        SELECT ?model ?operator ?date ?location ?phase ?weather
        WHERE {{
        ?drone rdf:type onto:Drone .
        ?drone onto:model ?model .
        ?drone onto:operator ?operator .
        ?drone onto:involvedInCrash ?crashEvent .
        ?crashEvent onto:date ?date .
        ?crashEvent onto:location ?location .
        ?crashEvent onto:phase ?phase .
        ?crashEvent onto:weather ?weather .
        FILTER(?phase = "{phase}")
        }}
        ORDER BY ?drone
    """
    
    results = g.query(query)
    
    data = []
    for row in results:
        row_dict = {}
        for var in results.vars:
            val = row[var]
            row_dict[str(var)] = str(val) if val else None
        data.append(row_dict)

@app.route('/filterDataByDate')
def filterDataByDate(date):
    date = request.args.get('date')
    g = Graph()
    g.parse("http://localhost:3030/droneCrashWeather/data", format="turtle")
    
    query = f"""
       PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX onto: <http://ubt/crashedDrones#>

        SELECT ?model ?operator ?date ?location ?phase ?weather
        WHERE {{
        ?drone rdf:type onto:Drone .
        ?drone onto:model ?model .
        ?drone onto:operator ?operator .
        ?drone onto:involvedInCrash ?crashEvent .
        ?crashEvent onto:date ?date .
        ?crashEvent onto:location ?location .
        ?crashEvent onto:phase ?phase .
        ?crashEvent onto:weather ?weather .
        FILTER(?date = "{date}")
        }}
        ORDER BY ?drone
    """
    
    results = g.query(query)
    
    data = []
    for row in results:
        row_dict = {}
        for var in results.vars:
            val = row[var]
            row_dict[str(var)] = str(val) if val else None
        data.append(row_dict)

    return jsonify(data)

@app.route('/filterAllDataWithWeatherCondition/<string:weather_condition>')
def filterAllDataWithWeatherCondition(weather_condition):

    weather_condition = weather_condition.capitalize()
    g = Graph()
    g.parse("http://localhost:3030/droneCrashWeather/data", format="turtle")
    
    query = f"""
       PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX onto: <http://ubt/crashedDrones#>

        SELECT ?model ?operator ?date ?location ?phase ?weather
        WHERE {{
        ?drone rdf:type onto:Drone .
        ?drone onto:model ?model .
        ?drone onto:operator ?operator .
        ?drone onto:involvedInCrash ?crashEvent .
        ?crashEvent onto:date ?date .
        ?crashEvent onto:location ?location .
        ?crashEvent onto:phase ?phase .
        ?crashEvent onto:weather ?weather .
        FILTER(?weather = "{weather_condition}")
        }}
        ORDER BY ?drone
    """
    
    results = g.query(query)
    
    data = []
    for row in results:
        row_dict = {}
        for var in results.vars:
            val = row[var]
            row_dict[str(var)] = str(val) if val else None
        data.append(row_dict)

    return jsonify(data)

@app.route('/getModelAndOperatorByPhase/<string:phase>')
def getModelAndOperatorByPhase(phase):

    phase = phase.capitalize()
    g = Graph()
    g.parse("http://localhost:3030/droneCrashWeather/data", format="turtle")
    
    query = f"""
       PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX onto: <http://ubt/crashedDrones#>

        SELECT ?operator ?model (COUNT(?crashEvent) AS ?crashCount)
        WHERE {{
        ?drone rdf:type onto:Drone .
        ?drone onto:model ?model .
        ?drone onto:operator ?operator .
        ?drone onto:involvedInCrash ?crashEvent .
        ?crashEvent onto:phase "{phase}" .
        }}
        GROUP BY ?operator ?model
        ORDER BY DESC(?crashCount)
        LIMIT 1
    """
    
    results = g.query(query)
    
    data = []
    for row in results:
        row_dict = {}
        for var in results.vars:
            val = row[var]
            row_dict[str(var)] = str(val) if val else None
        data.append(row_dict)

    return jsonify(data)

@app.route('/getModelAndOperatorByWeather/<string:weather_condition>')
def getModelAndOperatorByWeather(weather_condition):

    weather_condition = weather_condition.capitalize()
    g = Graph()
    g.parse("http://localhost:3030/droneCrashWeather/data", format="turtle")
    
    query = f"""
       PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX onto: <http://ubt/crashedDrones#>

        SELECT ?operator ?model (COUNT(?crashEvent) AS ?crashCount)
        WHERE {{
        ?drone rdf:type onto:Drone .
        ?drone onto:model ?model .
        ?drone onto:operator ?operator .
        ?drone onto:involvedInCrash ?crashEvent .
        ?crashEvent onto:weather "{weather_condition}" .
        }}
        GROUP BY ?operator ?model
        ORDER BY DESC(?crashCount)
        LIMIT 1
    """
    
    results = g.query(query)
    
    data = []
    for row in results:
        row_dict = {}
        for var in results.vars:
            val = row[var]
            row_dict[str(var)] = str(val) if val else None
        data.append(row_dict)

    return jsonify(data)

@app.route('/getOperatorWithMostCrashedByWeather/<string:weather_condition>')
def getOperatorWithMostCrashedByWeather(weather_condition):

    weather_condition = weather_condition.capitalize()
    g = Graph()
    g.parse("http://localhost:3030/droneCrashWeather/data", format="turtle")
    
    query = f"""
       PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX onto: <http://ubt/crashedDrones#>

        SELECT ?operator (COUNT(?crashEvent) AS ?crashCount)
        WHERE {{
        ?drone rdf:type onto:Drone .
        ?drone onto:operator ?operator .
        ?drone onto:involvedInCrash ?crashEvent .
        ?crashEvent onto:weather "{weather_condition}" .
        }}
        GROUP BY ?operator
        ORDER BY DESC(?crashCount)
        LIMIT 1
    """
    
    results = g.query(query)
    
    data = []
    for row in results:
        row_dict = {}
        for var in results.vars:
            val = row[var]
            row_dict[str(var)] = str(val) if val else None
        data.append(row_dict)

    return jsonify(data)

@app.route('/getLocationWithCrashedEvents')
def getLocationWithCrashedEvents():

    g = Graph()
    g.parse("http://localhost:3030/droneCrashWeather/data", format="turtle")
    
    query = f"""
       PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX onto: <http://ubt/crashedDrones#>

        SELECT (COUNT(?crashEvent) AS ?crashCount) ?location
        WHERE {{
        ?drone onto:involvedInCrash ?crashEvent .
        ?crashEvent onto:location ?location .
        }}
        GROUP BY ?location
    """
    
    results = g.query(query)
    
    data = []
    for row in results:
        row_dict = {}
        for var in results.vars:
            val = row[var]
            row_dict[str(var)] = str(val) if val else None
        data.append(row_dict)

    return jsonify(data)

@app.route('/getLocationWithMostCrashedEvents')
def getLocationWithMostCrashedEvents():

    g = Graph()
    g.parse("http://localhost:3030/droneCrashWeather/data", format="turtle")
    
    query = f"""
       PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX onto: <http://ubt/crashedDrones#>

        SELECT ?location (COUNT(?crashEvent) AS ?crashCount)
        WHERE {{
        ?crashEvent onto:location ?location .
        }}
        GROUP BY ?location
        ORDER BY DESC(?crashCount)
        LIMIT 1
    """
    
    results = g.query(query)
    
    data = []
    for row in results:
        row_dict = {}
        for var in results.vars:
            val = row[var]
            row_dict[str(var)] = str(val) if val else None
        data.append(row_dict)

    return jsonify(data)

@app.route('/getOperatorAndModelMostCrashedEventsInSpecificLocation/<string:location>')
def getOperatorAndModelMostCrashedEventsInSpecificLocation(location):

    location = location.capitalize()
    g = Graph()
    g.parse("http://localhost:3030/droneCrashWeather/data", format="turtle")
    
    query = f"""
       PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX onto: <http://ubt/crashedDrones#>

        SELECT ?model ?operator (COUNT(?crashEvent) AS ?crashCount)
        WHERE {{
        ?drone rdf:type onto:Drone .
        ?drone onto:model ?model .
        ?drone onto:operator ?operator .
        ?drone onto:involvedInCrash ?crashEvent .
        ?crashEvent onto:location "Komotini, Greece" .
        }}
        GROUP BY ?model ?operator
        ORDER BY DESC(?crashCount)
        LIMIT 1
    """
    
    results = g.query(query)
    
    data = []
    for row in results:
        row_dict = {}
        for var in results.vars:
            val = row[var]
            row_dict[str(var)] = str(val) if val else None
        data.append(row_dict)

    return jsonify(data)

@app.route('/getInWhichLocationHasMostCrashedFilterByModel/<string:model>')
def getInWhichLocationHasMostCrashedFilterByModel(model):

    model = model.capitalize()
    g = Graph()
    g.parse("http://localhost:3030/droneCrashWeather/data", format="turtle")
    
    query = f"""
       PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX onto: <http://ubt/crashedDrones#>

        SELECT ?location (COUNT(?crashEvent) AS ?crashCount)
        WHERE {{
        ?drone rdf:type onto:Drone .
        ?drone onto:model "{model}" .
        ?drone onto:involvedInCrash ?crashEvent .
        ?crashEvent onto:location ?location .
        }}
        GROUP BY ?location
        ORDER BY DESC(?crashCount)
        LIMIT 1
    """
    
    results = g.query(query)
    
    data = []
    for row in results:
        row_dict = {}
        for var in results.vars:
            val = row[var]
            row_dict[str(var)] = str(val) if val else None
        data.append(row_dict)

    return jsonify(data)

ReasonerFactory = autoclass("org.apache.jena.reasoner.ReasonerFactory")
Reasoner = autoclass("org.apache.jena.reasoner.Reasoner")
InfModel = autoclass("org.apache.jena.rdf.model.InfModel")

@app.route('/apply_rule')
def apply_rule():
    # Load the dataset
    g = Graph()
    g.parse("http://localhost:3030/droneCrashWeather/data", format="turtle")
    
    # Define the rule
    rule = """
    [] ns2:rule ""
    Drone(?d) ^ CrashEvent(?e) ^ involvedInCrash(?d, ?e) ^ weather(?e, "Heavy Rain/Snow") 
    -> hasRisk(?d, "High")
    "" .
    """
    
    # Load the rule into the dataset
    rule_ns = Namespace("http://ubt/crashedDrones#")
    g.bind("ns2", rule_ns)
    g.update(rule)
    
    # Create a reasoner
    reasonerFactory = ReasonerFactory.theInstance().create()
    reasoner = Reasoner(reasonerFactory)
    
    # Apply reasoning
    infModel = InfModel(reasoner, g)
    
    # Trigger the reasoning process
    reasoning_query = """
    PREFIX ns2: <http://ubt/crashedDrones#>
    SELECT ?d
    WHERE {
        ?d ns2:hasRisk "High" .
    }
    """
    
    # Execute the reasoning query
    reasoning_results = infModel.query(reasoning_query)
    
    inferred_triples = []
    for row in reasoning_results:
        inferred_triples.append(row[0])
    
    # You can return or further process the inferred triples here
    return jsonify(inferred_triples)


if __name__ == '__main__':
    app.run(debug=True)
