<script>

	import { onMount } from "svelte";
	import maplibregl from "maplibre-gl";
	import "maplibre-gl/dist/maplibre-gl.css";
	import * as pmtiles from "pmtiles";
	import "../assets/global.css";
	import dotCity from "../assets/sofc-long-city.svg";
	import sofcLogo from "../assets/top-logo-full.svg";
	import current_lines from "../data/current-lines.geo.json";
	import future_lines from "../data/future-lines.geo.json";
	import currentstations from "../data/current-stations.geo.json";
	import futurestations from "../data/future-stations.geo.json";
	import Select from "svelte-select";
	import hatch from "../assets/hatch-pattern-low-sample.png";
	import mapLabels from "../assets/map-labels.json";
    import filter from "svelte-select/filter";

	let PMTILES_URL = 'https://api.protomaps.com/tiles/v4.json?key=7f48bb9c6a1f1e3b';
	let LAYERS_URL = 'map-layers.pmtiles';
	let TTS_URL = "tts2022zones_data.pmtiles";

	let map = null;

	let colours_yellowred = ["#f1c500", "#eca50d", "#e7861a", "#e16626", "#DC4633"];
	let colours_greens = ['#eafffc','#6cccbe','#00a189','#067c6c','#0d534d'];
	let colours_bluepurple = ['#cdf1ff', '#9acef4', '#6fb1ea', '#6e6db4', '#6d247a']

	const defaultMap = "% of trips by walking";
	let mapSelected = defaultMap;

	let data = "TTS";

	let ttsZone = "";
	let ttsValue = "NA"
	let lastHoveredZone = null; 

	const choropleths = {
		"Vehicles per household": {
			dataSource: "veh_per_hhld",
			breaks: [0.5, 1, 1.5, 2],   
			colours: colours_bluepurple,
			text: "Average number of private vehicles per household."
		},
		"Driver's license per person": {
			dataSource: "drivers_lic_perperson_20to75",
			breaks: [75, 80, 85, 90],   
			colours: colours_bluepurple,
			text: "Percent of residents aged 20 to 75 that have a driver's license."
		},
		// "Transit pass per person": {
		// 	dataSource: "transpass_perperson_6up",
		// 	breaks: [5, 10, 15, 20],   
		// 	colours: colours_bluepurple,
		// 	text: "Percent of residents aged 6 and up that have a transit pass"
		// },
		"% of trips by bicycle": {
			dataSource: "mode_bike",
			breaks: [2, 4, 8, 16],   
			colours: colours_bluepurple,
			text: "Percentage of trips made by residents of this zone that are taken by bicycle."
		},
		"% of trips by walking": {
			dataSource: "mode_walk",
			breaks: [5, 15, 30, 50],   
			colours: colours_bluepurple,
			text: "Percentage of trips made by residents of this zone that are solely pedestrian/walking trips."
		},
		"% of trips by public transit": {
			dataSource: "mode_transit",
			breaks: [5, 10, 20, 30],
			colours: colours_bluepurple,
			text: "Percentage of trips made by residents of this zone that are by public transit. These trips can include different access and egress modes, but the main mode is public transit."
		},
		"% of trips by car": {
			dataSource: "mode_drive",
			breaks: [50, 65, 80, 90],   
			colours: colours_bluepurple,
			text: "Percentage of trips made by residents of this zone that are by car. These include trips as a driver or as a passenger, including all taxi/ride-share trips)"
		},
		"Average trip distance (km)": {
			dataSource: "trip_km_avg",
			breaks: [5, 10, 15, 20],   
			colours: colours_bluepurple,
			text: "Average straight line (i.e. Euclidean) distance of trips made by households in this zone (i.e. how far to people travel on average on a per trip basis)"
		},
		"Trips per person": {
			dataSource: "trips_5up_per_person",
			breaks: [1.75, 2, 2.25, 2.5],   
			colours: colours_bluepurple,
			text: "Average number of trips people live in this zone make per day"
		},
		"Activity participation": {
			dataSource: "activities_mean",
			breaks: [0.8, 1, 1.2, 1.4],   
			colours: colours_bluepurple,
			text: "Average number of activity destinations people visit per day among people who live in this zone. This has been used as a measure of transport-related social inclusion/exclusion."
		},
		"% of trips that are local trips": {
			dataSource: "trips_less5km_percent",
			breaks: [20, 40, 60, 80],   
			colours: colours_bluepurple,
			text: "Percentage of trips made by residents of this zone that are less than 5km in length. In other words, what proportion of trips do people make that are local"
		},
		"% of local trips by car": {
			dataSource: "trips_less5km_percent_car",
			breaks: [20, 40, 60, 80],   
			colours: colours_bluepurple,
			text: "Of local trips made by residents that live in this zone (i.e. of trips less than 5km in length), what percent are by car. In other words, how car dependent are residents on cars for local trips"
		},
		"% of children driven to/from school": {
			dataSource: "children_driven_to_school",
			breaks: [5, 20, 35, 50],   
			colours: colours_bluepurple,
			text: "Percent of home-school trips by children (ages 6-17) that are by car"
		}
	};

	const items = Object.keys(choropleths).map((key) => {
		return {
			label: key,
			value: key
		}
	});

	let mapLoaded = false;
	let isMapReady = false;

	let pendingLayerSelectCalls = [];

	function processPendingLayerSelectCalls() {
    	if (map && mapLoaded && isMapReady && map.isStyleLoaded()) {
        	while (pendingLayerSelectCalls.length > 0) {
            	const e = pendingLayerSelectCalls.shift(); // Get the next pending call
            	layerSelect(e); // Process the call
        	}
    	}
	}
	
	function layerSelect(e) {
		console.log("layerSelect called with:", e.detail);

    	if (!map || !mapLoaded || !isMapReady || !map.isStyleLoaded()) {
        	console.warn("Map is not ready. Adding to queue...");
			pendingLayerSelectCalls.push(e);
        	return;
    	};

    	console.log("Setting layer:", e.detail.value);
    	mapSelected = e.detail.value;
    	layerSet(mapSelected);
	}		

	function layerSet(layer) {
		
		let choropleth = choropleths[layer];
		console.log(choropleth);

		map.setPaintProperty("ttszones", "fill-opacity", 0.8);
		map.setPaintProperty("ttszones", "fill-color", [
			"case",
			["==", ["get", choropleth.dataSource], null], "#c0bfbc",
			["step", ["get", choropleth.dataSource],
			choropleth.colours[0], choropleth.breaks[0],
			choropleth.colours[1], choropleth.breaks[1],
			choropleth.colours[2], choropleth.breaks[2],
			choropleth.colours[3], choropleth.breaks[3],
			choropleth.colours[4]]			
		]);
		// map.setPaintProperty('ttszones-pattern', 'fill-pattern', 'pattern');
	}

	let onTransit = true;

	$:  onTransit, filterTransit()

	function filterTransit() {
		if (map) {
			if (onTransit) {
				map.setPaintProperty('current_lines', 'line-opacity', 1);
				map.setPaintProperty('currentstations', 'circle-opacity', 1);
				map.setPaintProperty('currentstations', 'circle-stroke-opacity', 1);
			} else {
				map.setPaintProperty('current_lines', 'line-opacity', 0);
				map.setPaintProperty('currentstations', 'circle-opacity', 0);
				map.setPaintProperty('currentstations', 'circle-stroke-opacity', 0);
			}
		}
	}

	let onTransitFuture = false;

	$:  onTransitFuture, filterTransitFuture()

	function filterTransitFuture() {
		if (map) {
			if (onTransitFuture) {
				map.setPaintProperty('future_lines', 'line-opacity', 1);
				map.setPaintProperty('futurestations', 'circle-opacity', 1);
				map.setPaintProperty('futurestations', 'circle-stroke-opacity', 1);
			} else {
				map.setPaintProperty('future_lines', 'line-opacity', 0);
				map.setPaintProperty('futurestations', 'circle-opacity', 0);
				map.setPaintProperty('futurestations', 'circle-stroke-opacity', 0);
			}
		}
	}

	let onHighways = false;

	$: onHighways, filterHighways()

	function filterHighways() {
		if (map) {
			if (onHighways) {
				map.setPaintProperty('highways', 'line-opacity', 1);
			} else {
				map.setPaintProperty('highways', 'line-opacity', 0);
			}
		}
	}

	let onBicycle = false;

	$: onBicycle, filterBicycle()

	function filterBicycle() {
		if (map) {
			if (onBicycle) {
				map.setPaintProperty('bikes', 'line-opacity', 1);
			} else {
				map.setPaintProperty('bikes', 'line-opacity', 0);
			}
		}
	}



	onMount(async () => {

		let protocol = new pmtiles.Protocol();
		maplibregl.addProtocol("pmtiles", protocol.tile);

		map = new maplibregl.Map({
			container: "map",
			style: 
			// https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
			{
				version: 8,
				name: "Empty",
				glyphs: "https://schoolofcities.github.io/fonts/fonts/{fontstack}/{range}.pbf", // our fonts, switch back in when we have our own style
				// glyphs:'https://protomaps.github.io/basemaps-assets/fonts/{fontstack}/{range}.pbf',
    			sprite: "https://protomaps.github.io/basemaps-assets/sprites/v4/dark",
				sources: {
					'protomaps': {
						type: 'vector',
						url: 'https://api.protomaps.com/tiles/v4.json?key=f1d93c3bd5c79742'
					}
				},
				layers: [
					{
						"id": "background",
						"type": "background",
						"layout": {
							"visibility": "visible"
						},
							"paint": {
							"background-color": "#f6f5f4",
							"background-opacity": 1
						}
					}
				]
			},
			
			maxPitch: 0,
			maxZoom: 14,
			minZoom: 8,
			center: [-79.44, 43.72],
			zoom: 10,

			// projection: "globe",
			scrollZoom: false,
			dragPan: true,
			dragRotate: false,
			doubleClickZoom: true,
			// touchZoomRotate: false,
			// keyboard: false,
			// interactive: false,
			attributionControl: false,

		});

		map.on('load', async () => {

			const nav = new maplibregl.NavigationControl({
				showCompass: false,  // Optional: Hides the compass
				showZoom: true       // Shows zoom buttons
			});
			map.addControl(nav, 'top-left');

			map.addSource('ttszones', {
				type: "vector",
                url: "pmtiles://" + TTS_URL,
			});

			map.addSource('maplayers', {
				type: "vector",
                url: "pmtiles://" + LAYERS_URL,
			});

			// map.addSource('lowertier', {
			// 	type: 'geojson',
			// 	data: lowertier
			// });

			// map.addSource('uppertier', {
			// 	type: 'geojson',
			// 	data: uppertier
			// });


			map.addSource('current_lines', {
				type: 'geojson',
				data: current_lines
			});

			map.addSource('future_lines', {
				type: 'geojson',
				data: future_lines
			});

			map.addSource('currentstations', {
				type: 'geojson',
				data: currentstations
			});

			map.addSource('futurestations', {
				type: 'geojson',
				data: futurestations
			});

			map.addLayer(
				{
					'id': 'ttszones',
					'type': 'fill',
					'source': 'ttszones',
					"source-layer": "tts2022zones_data",
				}
			);

			map.addLayer(
				{
					"id": "water",
					"type": "fill",
					"filter": [
						"==",
						[
						"geometry-type"
						],
						"Polygon"
					],
					"source": "protomaps",
					"source-layer": "water",
					"paint": {
						"fill-color": "#fff",
						"fill-opacity": 1
					}
				}
			)

			map.addLayer(
				{
					"id": "roads_minor",
					"type": "line",
					"source": "protomaps",
					"source-layer": "roads",
					"filter": [
					"all",
					[
						"==",
						"kind",
						"minor_road"
					],
					[
						"!=",
						"kind_detail",
						"service"
					]
					],
					"minzoom": 11,
					"paint": {
					"line-opacity": 0.3,
					"line-color": "#d0cfce",
					"line-width": [
						"interpolate",
						[
						"exponential",
						1.6
						],
						[
						"zoom"
						],
						11, 0,
						12.5, 0.5,
						15,	4
					]
					}
				}
			)

			map.addLayer(
				{
					"id": "roads_major",
					"type": "line",
					"source": "protomaps",
					"source-layer": "roads",
					"filter": [
						"any",
						[
							"==",
							"kind",
							"major_road"
						],
						[
							"==",
							"kind",
							"highway"
						]
					],
					"minzoom": 10,
					"paint": {
						"line-opacity": 0.3,
						"line-color": "#d0cfce",
						"line-width": [
						"interpolate",
						[
							"exponential",
							1.6
						],
						[
							"zoom"
						],
						7,	0,
						12,	2,
						15,	4,
						]
					}
				}
			)

			map.addLayer(
				{
					'id': 'lowertier',
					'type': 'line',
					'source': 'maplayers',
					'source-layer': 'Lower_Tier',
					'paint': {
						'line-color': '#fff',
						'line-width': ['interpolate', ['linear'], ['zoom'], 7, 0.5, 10, 3]
					}
				}
			);

			map.addLayer(
				{
					'id': 'uppertier',
					'type': 'line',
					'source': 'maplayers',
					'source-layer': 'Upper_Single_Tier',
					'paint': {
						'line-color': '#fff',
						'line-width': ['interpolate', ['linear'], ['zoom'], 7, 1, 10, 6],
						
					}
				}
			);

			map.addLayer(
				{
					"id": "highways",
					"type": "line",
					"source": "protomaps",
					"source-layer": "roads",
					"filter": [
						"any",
						[
							"==",
							"kind",
							"highway"
						],
						[
							"==",
							"kind_detail",
							"trunk"
						],
						[
							"==",
							"kind_detail",
							"trunk_link"
						]
					],
					"paint": {
						"line-opacity": 0,
						"line-color": "#ce6456",
						"line-width": [
						"interpolate",
						[
							"exponential",
							1.6
						],
						[
							"zoom"
						],
						7, 1,
						15,	5,
						]
					}
				}
			)

			map.addLayer(
				{
					'id':'bikes',
					'type':'line',
					'source':'maplayers',
					'source-layer':'CanBICS_wgs84',
					'paint': {
						'line-color': '#00A189',
						'line-width': ['interpolate', ['linear'], ['zoom'], 9, 0.5, 14, 3],
						'line-opacity': 0 
					}
				}
			);

			map.addLayer(
				{
					'id':'current_lines',
					'type':'line',
					'source':'current_lines',
					'paint': {
						'line-color': '#1E3765',
						'line-width': ['interpolate', ['linear'], ['zoom'], 9, 1, 14, 4] 
					}
				}
			);

			map.addLayer(
				{
					'id':'future_lines',
					'type':'line',
					'source':'future_lines',
					'paint': {
						'line-color': '#1E3765',
						'line-width': ['interpolate', ['linear'], ['zoom'], 9, 1, 14, 4],
						'line-dasharray': [4, 2],
						'line-opacity': 0
					}
				}
			);

			map.addLayer(
				{
					'id': 'currentstations',
					'type': 'circle',
					'source': 'currentstations',
					'paint': {
						'circle-radius': ['interpolate', ['linear'], ['zoom'], 8, 1, 16, 6],
						'circle-color': '#1E3765',
						'circle-stroke-color': '#ffffff',
						'circle-stroke-width': ['interpolate', ['linear'], ['zoom'], 8, 0, 11, 1],
					}
				}
			);

			map.addLayer(
				{
					'id': 'futurestations',
					'type': 'circle',
					'source': 'futurestations',
					'paint': {
						'circle-radius': ['interpolate', ['linear'], ['zoom'], 8, 1, 16, 6],
						'circle-color': '#1E3765',
						'circle-stroke-color': '#ffffff',
						'circle-stroke-width': ['interpolate', ['linear'], ['zoom'], 8, 0, 11, 1],
						'circle-opacity': 0,
						'circle-stroke-opacity': 0
					}
				}
			);

			map.addLayer({
				"id": 'outline-hover',
				"type": 'line',
				'source': 'ttszones',
				"source-layer": "tts2022zones_data",
				"paint": {
					'line-color': '#AB1368',
					'line-width': 2,
				},
				"filter": ['==', 'TTS2022', ''],
			});

			mapLabels.forEach(style => {
				map.addLayer(style);
			});

			fetch(hatch)
				.then(response => response.blob())
				.then(blob => createImageBitmap(blob))
				.then(image => {
					map.addImage('polygon-pattern', image, { pixelRatio: 1 });
					console.log("Image loaded via fetch!");
					map.addLayer({
						'id': 'tts-low-sample',
						'type': 'fill',
						'source': 'ttszones',
						"source-layer": "tts2022zones_data",
						'paint': {
							'fill-pattern': 'polygon-pattern',
						},
						'filter': [
							'any',
							['!', ['has', 'hhld_sample']] ,
							['<', ['get', 'hhld_sample'], 10]
						]
					}, 'lowertier');
					map.addLayer(
						{
							'id': 'ttszones_lines',
							'type': 'line',
							'source': 'ttszones',
							'source-layer': 'tts2022zones_data',
							'minzoom': 9,
							'paint': {
								'line-width': [
									'interpolate',            
									['linear'],               
									['zoom'],                
									8, 0,
									9, 0.5,                   
									10, 0.9                   
								],
								'line-color': '#fff'
							},
					}, 'lowertier');

					

				})
				.catch(error => console.error("Error fetching image:", error));			


			console.log("Map loaded successfully.");
			mapLoaded = true;
			
			map.once('styledata', () => {
				console.log("Map style fully loaded.");
				isMapReady = true;
				layerSet(defaultMap);
				processPendingLayerSelectCalls();
			});
		});

		// const popup = new maplibregl.Popup({
		// 	closeButton: false,
		// 	closeOnClick: false
		// });

		
		let lastUpdate = 0;
		map.on('mousemove', 'ttszones', (e) => {
			const now = performance.now();
			if (now - lastUpdate < 100) return;
			lastUpdate = now;

			map.getCanvas().style.cursor = 'pointer';
			
			if (!e.features.length) return;
			
			const properties = e.features[0].properties;
			const currentZone = properties.TTS2022;
			
			if (currentZone !== ttsZone) {

				map.setFilter('outline-hover', ['==', 'TTS2022', currentZone]);
				
				ttsValue = (properties[choropleths[mapSelected].dataSource] >= 0) 
					? Math.round(properties[choropleths[mapSelected].dataSource] * 10) / 10
					: "No Data";
				
				ttsZone = currentZone;
			}
		});

		map.on('mouseleave', 'ttszones', () => {
			map.getCanvas().style.cursor = '';
			ttsValue = "no data";
			ttsZone = "";
			map.setFilter('outline-hover', ['==', 'TTS2022', '']);
		});

		map.on('error', (error) => {
			console.error("Map load error:", error);
		});

		let scale = new maplibregl.ScaleControl({
			maxWidth: 100,
			unit: "metric",
		});

		map.addControl(scale, "bottom-right");
	
	});

	

</script>

<div id='container'>

	<div id='panel'>

		<img src={dotCity} alt="dot city" style="padding-left: 20px" />

		<h1>Greater Golden Horseshoe</h1>

		<h2>Mapping data about the region's transportation geography and travel patterns</h2>

		<div id="line"></div>

		<div id="line"></div>

		<div id='select-wrapper'>
			{#if map && mapLoaded && isMapReady}
				<Select
					id='select'
					items={items}
					value={mapSelected}
					clearable={false}
					showChevron={true}
					listAutoWidth={true}
					searchable={false}
					listOffset = 10
					on:change={layerSelect}
				/>
			{:else}
				<p>Loading map...</p>
			{/if}
		</div>

		<svg width='400' height='40'>
			<rect
			class = "box"
			width="74"
			height="20"
			x="18"
			y="0"
			style="fill:{choropleths[mapSelected].colours[0]};"
			/>
	
			<rect
			class = "box"
			width="74"
			height="20"
			x="94"
			y="0"
			style="fill:{choropleths[mapSelected].colours[1]};"
			/>
	
			<rect
			class = "box"
			width="74"
			height="20"
			x="170"
			y="0"
			style="fill:{choropleths[mapSelected].colours[2]};"
			/>
	
			<rect
			class = "box"
			width="74"
			height="20"
			x="246"
			y="0"
			style="fill:{choropleths[mapSelected].colours[3]};"
			/>
	
			<rect
			class = "box"
			width="74"
			height="20"
			x="322"
			y="0"
			style="fill:{choropleths[mapSelected].colours[4]};"
			/>
	
			<text class="legend-label"  x="80" y="35">&lt;{choropleths[mapSelected].breaks[0]}</text>
			<text class="legend-label"  x="160" y="35">{choropleths[mapSelected].breaks[1]}</text>
			<text class="legend-label"  x="235" y="35">{choropleths[mapSelected].breaks[2]}</text>
			<text class="legend-label"  x="305" y="35">&gt{choropleths[mapSelected].breaks[3]}</text>
	
		</svg>

		<p class="des">
			{choropleths[mapSelected].text}
		</p>

		

		<p class="des">

			<span style="
				display: inline-flex;
				align-items: center;
				gap: 8px;
			">
				<span style="
					width: 30px;
					height: 16px;
					background: url('{hatch}') repeat;
					background-size: 6px 6px;
					background-color: #6FC7EA;
					opacity: 0.8;
					"
				/>
				<span style="font-size: 14px">Low sample (n {"<"} 10) </span>
			</span>
		
			<span style="
				display: inline-flex;
				align-items: center;
				gap: 8px;
			">
				<span style="
					margin-left: 7px;
					width: 30px;
					height: 16px;
					background: url('{hatch}') repeat;
					background-size: 6px 6px;
					background-color: #D0D1C9;
					opacity: 0.8;
					"
				/>
				<span style="font-size: 14px">No data</span>
			</span>

		</p>

		<p  class="des" style="font-size: 11px; color: #AB1368; padding-bottom; -20px">
			Selected zone
		</p>
		<p class="des" style="font-size: 13px; padding: 4px; border: solid 1px #AB1368; margin-top: -10px;">
			{mapSelected}: {ttsValue}
		</p>

		<div id="line"></div>

		<div id="checkbox" class="check-box">
			<label class="label-format"><input type="checkbox" class="check-box-item" bind:checked={onTransit}/> 
				Major transit routes (GO, Subway, LRT)
				<svg width="30" height="12">
					<line x1="0" y1="6" x2="40" y2="6" stroke="#1E3765" stroke-width="2"/>
					<circle cx="15" cy="6" r="4" fill="#1E3765", stroke="#ffffff" stroke-width="2"/>
				</svg>
			</label>
			<br>
			<label class="label-format"><input type="checkbox" class="check-box-item" bind:checked={onTransitFuture}/> 
				Major transit routes under development
				<svg width="30" height="12">
					<line x1="0" y1="6" x2="40" y2="6" stroke="#1E3765" stroke-width="2" stroke-dasharray="4,1"/>
					<circle cx="15" cy="6" r="4" fill="#1E3765", stroke="#ffffff"  stroke-width="2"/>
				</svg>
			</label>
			<br>
			<label class="label-format"><input type="checkbox" class="check-box-item" bind:checked={onHighways}/> 
				Major highways 
				<svg width="30" height="12">
					<line x1="0" y1="8" x2="40" y2="8" stroke="#DC4633" stroke-width="3" opacity="0.5"/>
				</svg>
			</label>
			<br>
			<label class="label-format"><input type="checkbox" class="check-box-item" bind:checked={onBicycle}/> 
				Cycling infrastructure
				<svg width="30" height="12">
					<line x1="0" y1="8" x2="40" y2="8" stroke="#00A189" stroke-width="3" opacity="0.95"/>
				</svg>
			</label>
		</div>

		<div id="line"></div>

		<div id="line"></div>

		<p class="notes">
			These maps were created by <a href="https://jamaps.github.io" target="_blank">Jeff Allen</a> and <a href="https://mkbs-mkbs2000.github.io/Personal-Portfolio/">Muhammad Khalis Bin Samion</a> at the <a href="https://schoolofcities.utoronto.ca/" target="_blank">School of Cities, University of Toronto</a>.
		</p>

		<p class="notes">
			All the travel-related data are from the <a href="https://dmg.utoronto.ca/tts-introduction/" target="_blank">2022 Transportation Tomorrow Survey</a>. The base-map data pertaining to roads and water are from <a href="https://www.openstreetmap.org/" target="_blank">OpenStreetMap</a>. Cycling data are from <a href="https://chatrlab.ca/projects/can-bics-english/" target="_blank">Can-BICS (CHATR Lab)</a> and include bike lanes, cycle tracks, and trails. Transit route data are from <a href="https://www.metrolinx.com/en/about-us/open-data" target="_blank">Metrolinx</a>. 
		</p>

		<p class="notes">
			If there's anything on this map you have questions about, have feedback for ways to improve it, or want to see additional data on the map, please add an issue on the <a href="https://github.com/schoolofcities/ggh-transport-geography" target="_blank">GitHub page</a> or just email us directly. Thank you! :)
		</p>

		<a href="https://schoolofcities.utoronto.ca/" target="_blank">
			<img 
				src={sofcLogo} 
				alt="School of Cities logo" 
				style="display: block; margin: 0 auto; width: 300px; height: auto; opacity: 0.8"
				on:mouseover={() => (event.target.style.opacity = 1)}
   				on:mouseout={() => (event.target.style.opacity = 0.8)}
			/>
		</a>
		
		<br>

	</div>

	<div id="map"></div>

</div>


<style>

	#container {
		display: flex;
		flex-direction: row; 
	}

	#panel {
		max-width: 420px;
		width: 100%;
		min-width: 350px;
		height: calc(100vh - 15px);
		overflow-y: auto;
		/* overflow-x: hidden; */
		background-color: var(--brandWhite);
		padding-top: 15px;
		border-right: solid 1px var(--brandLightBlue);
		flex-shrink: 0;
	}

	#map {
		flex: 1;
		height: 100vh;
		overflow: hidden;
	}

	/* Mobile layout at 840px or below */
	@media (max-width: 840px) {
		#container {
			flex-direction: column;
			height: 100vh;
		}

		#panel {
			max-width: 840px;
			width: 100%;
			height: 50vh;
			border-right: none; 
			order: 2;
		}

		#map {
			border-bottom: solid 1px var(--brandLightBlue);
			width: 100%;
			height: 50vh;
			order: 1;
		}
	}


	#select-wrapper {
		--margin: 16px;
		--width: 380px;
		--multi-max-width: 300px;
		--background: white;
		--selected-item-color: #000000;
		--height: 22px;
		--item-color: #000000;
		--border-radius: 0px;
		--border: 1px solid #cbcbcb;
		--border-focused: 1px solid #6FC7EA;
		--list-border-radius: 0px;
		--font-size: 13.7px;
		--font-family: Roboto;
		--max-height: 30px;
		--item-is-active-color: #FFFFFF;
		--item-is-active-bg: #007FA3;
		--chevron-color: #1E3765;
		--item-hover-bg: #F1C500;
	}

	.des {
		margin-top: 4px;
		margin-left: 20px;
		margin-right: 20px;
		font-size: 14px;
		line-height: 18px;
	}

	.notes {
		margin-top: 4px;
		margin-left: 20px;
		margin-right: 20px;
		font-size: 13px;
		line-height: 17px;
	}

	#checkbox {
		padding-left: 15px;
	}

	.label-format {
		font-size: 14px;
		line-height: 18px;
		color: var(--brandDarkBlue);
	}

	#line {
		height: 1px;
		width: 100%;
		background-color: var(--brandLightBlue);
		margin-top: 10px;
		margin-bottom: 10px
	}

	img:hover {
		opacity: 1;
	}


</style>
