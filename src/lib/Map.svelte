<script>

	import { onMount } from "svelte";
	import maplibregl from "maplibre-gl";
	import "maplibre-gl/dist/maplibre-gl.css";
	import * as pmtiles from "pmtiles";
	import layers from 'protomaps-themes-base';
	import "../assets/global.css";
	import current_lines from "../data/current-lines.geo.json";
	import future_lines from "../data/future-lines.geo.json";
	import currentstations from "../data/current-stations.geo.json";
	import futurestations from "../data/future-stations.geo.json";
	import Select from "svelte-select";
	import lowertier from "../data/TTS_Lower_Tier.geo.json";
	import uppertier from "../data/TTS_Upper_Single_Tier.geo.json";
	import hatch from "../assets/hatch-pattern-low-sample.png";

	let PMTILES_URL = 'https://api.protomaps.com/tiles/v4.json?key=7f48bb9c6a1f1e3b'
	let TTS_URL = "tts2022zones_data.pmtiles"

	let map = null;

	let colours_yellowred = ["#f1c500", "#eca50d", "#e7861a", "#e16626", "#DC4633"];
	let colours_greens = ['#eafffc','#6cccbe','#00a189','#067c6c','#0d534d'];
	let colours_bluepurple = ['#cdf1ff', '#9acef4', '#6fb1ea', '#6e6db4', '#6d247a']

	const defaultMap = "% Trips by walking";
	let mapSelected = defaultMap;

	const choropleths = {
		"% Trips by bicycle": {
			dataSource: "mode_bike",
			breaks: [2, 4, 8, 16],  // using natural jenks breaks
			colours: colours_bluepurple,
			text: "% of trips by people who live in this zone that are by bicycle"
		},
		"% Trips by walking": {
			dataSource: "mode_walk",
			breaks: [5, 15, 30, 50],  // using natural jenks breaks
			colours: colours_bluepurple,
			text: "% of trips by people who live in this zone that are by foot"
		},
		"% Trips by public transit": {
			dataSource: "mode_transit",
			breaks: [5, 10, 25, 50],
			colours: colours_bluepurple,
			text: "% of trips by people who live in this zone that are by public transit"
		},
		"% Trips by car": {
			dataSource: "mode_drive",
			breaks: [50, 65, 80, 90],  // using natural jenks breaks
			colours: colours_bluepurple,
			text: "% of trips by people who live in this zone that are by car (including as a driver or passenger)"
		},
		"Activity Participation": {
			dataSource: "activities_mean",
			breaks: [0.8, 1, 1.2, 1.4],  // using natural jenks breaks
			colours: colours_bluepurple,
			text: "Average number of activity destinations people visit per day"
		},
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
				// glyphs: "https://schoolofcities.github.io/fonts/fonts/{fontstack}/{range}.pbf", // our fonts, switch back in when we have our own style
				glyphs:'https://protomaps.github.io/basemaps-assets/fonts/{fontstack}/{range}.pbf',
    			sprite: "https://protomaps.github.io/basemaps-assets/sprites/v4/dark",
				sources: {
					'protomaps': {
						type: 'vector',
						url: 'https://api.protomaps.com/tiles/v4.json?key=f1d93c3bd5c79742',
						attribution: '<a href="https://protomaps.com">Protomaps</a> © <a href="https://openstreetmap.org">OpenStreetMap</a>'
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
			center: [-79.45, 43.75],
			zoom: 10,

			// variety of map interactivity/display settings to change later
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

			

			map.addSource('lowertier', {
				type: 'geojson',
				data: lowertier
			});

			map.addSource('uppertier', {
				type: 'geojson',
				data: uppertier
			});


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

			// map.addLayer(
			// 	{
			// 		"id": "water_outline",
			// 		"type": "line",
			// 		"filter": [
			// 			"==",
			// 			[
			// 			"geometry-type"
			// 			],
			// 			"Polygon"
			// 		],
			// 		"source": "protomaps",
			// 		"source-layer": "water",
			// 		"paint": {
			// 			"line-opacity": 1,
			// 			"line-color": "#bebdbb",
			// 			"line-width": 0.3
			// 		}
			// 	}
			// )

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
					'source': 'lowertier',
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
					'source': 'uppertier',
					'paint': {
						'line-color': '#fff',
						'line-width': ['interpolate', ['linear'], ['zoom'], 7, 1, 10, 6],
						
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
						'line-width': ['interpolate', ['linear'], ['zoom'], 7, 1, 16, 2] 
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
						'line-width': ['interpolate', ['linear'], ['zoom'], 7, 1, 16, 2],
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

			// hatch pattern on low sample
			fetch(hatch)
				.then(response => response.blob())
				.then(blob => createImageBitmap(blob))
				.then(image => {
					map.addImage('polygon-pattern', image, { pixelRatio: 1 });
					console.log("Image loaded via fetch!");
					map.addLayer({
						'id': 'polygon-layer',
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

				
			


			

			/*const image = await map.loadImage('https://png.pngtree.com/png-vector/20210224/ourmid/pngtree-diagonal-black-stripes-png-image_2933503.jpg');

			map.addImage('pattern', image.data);

			map.addLayer({
				id: 'ttszones-pattern',
				type: 'fill',
				source: 'ttszones',
				paint: {
					'fill-pattern': 'pattern',
					'fill-opacity': 0.6
				}
			});*/

			

			console.log("Map loaded successfully.");
			mapLoaded = true;
			
			map.once('styledata', () => {
				console.log("Map style fully loaded.");
				isMapReady = true;
				layerSet(defaultMap);
				processPendingLayerSelectCalls();
			});
		});

		const popup = new maplibregl.Popup({
			closeButton: false,
			closeOnClick: false
		});

		map.on('mousemove', 'ttszones', (e) => {
			map.getCanvas().style.cursor = 'pointer';

    		const properties = e.features[0].properties; // Extract properties from the feature

    		// Create the popup content
    		const description = 
    		`<strong>TTS Zone ${properties.TTS2022}</strong><br>
    		Population Density: ${properties.Pop_Dens}<br>
    		No-Vehicle Household Rate (in %): ${properties.Perc_No_Veh}<br>
    		Vehicle per Household Rate: ${properties.Veh_Per_Hhld}`;

    		// Get map container dimensions
    		const container = map.getContainer();
    		const width = container.offsetWidth;
    
    		// Position popup in top-right corner (adjust padding as needed)
    		popup.setLngLat([0, 0]) // Dummy coordinates (won't be used)
			.setHTML(description)
          	.addTo(map);
    
		    // Manually position the popup element
    		const popupElement = popup.getElement();
    		popupElement.style.position = 'absolute';
    		popupElement.style.top = '10px';
    		popupElement.style.right = '10px';
    		popupElement.style.left = 'auto';
    		popupElement.style.transform = 'none';
		});

		map.on('mouseleave', 'ttszones', () => {
			map.getCanvas().style.cursor = '';
			popup.remove();
		});

		map.on('error', (error) => {
			console.error("Map load error:", error);
		});

		const attributions = [
			'<a href="https://openstreetmap.org" target= "_blank" style="color: black; text-decoration: underline;"> OpenStreetMap</a>'
		];
		const attributionString = attributions.join(", ");

		map.addControl(
			new maplibregl.AttributionControl({
				compact: false,
			}),
			'bottom-right'
		);

		let scale = new maplibregl.ScaleControl({
			maxWidth: 100,
			unit: "metric",
		});

		map.addControl(scale, "bottom-right");
	
	});

</script>

<div id='container'>

	<div id='panel'>

		<div id='title'>

			<h1>Transportation Tomorrow Survey</h1>

			<h2>Results across the Greater Golden Horseshoe Region</h2>

			<img src={hatch} alt="Hatch pattern" />

		</div>

		<h3>Select Layers</h3>

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

		<h3>Select Other Reference Layers</h3>

		<div id="checkbox" class="check-box">
			<label class="label-format"><input type="checkbox" class="check-box-item" bind:checked={onTransit}/> 
				Existing Transit Lines
				<svg width="30" height="12">
					<line x1="0" y1="6" x2="40" y2="6" stroke="#002FD8" stroke-width="4.5"/>
					<circle cx="15" cy="6" r="4" fill="#002FD8", stroke="#ffffff"/>
				</svg>
			</label>
			<br>
			<label class="label-format"><input type="checkbox" class="check-box-item" bind:checked={onTransitFuture}/> 
				Upcoming Transit Lines
				<svg width="30" height="12">
					<line x1="0" y1="6" x2="40" y2="6" stroke="#00CCFF" stroke-width="4.5"/>
					<circle cx="15" cy="6" r="4" fill="#00CCFF", stroke="#000000"/>
				</svg>
			</label>
		</div>

	</div>

	<div id="map"></div>

</div>


<style>

	#container {
		display: flex;
	}

	#panel {
		width: 420px;
		min-width: 420px;
		height:100vh;
		overflow: auto;
		overflow-x: hidden;
		background-color: #F0FFFF;
		border-left: 10px;
	}

	#title {
		text-decoration: none;
		margin-left: 16px;
		margin-bottom: 0px;
		margin-right: 16px;
		margin-top: 17px;
		padding: 10px;
		text-align: center;
		background-color: #007FA3;
	}

	#panel h3 {
		color: #000000;
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
		--border-focused: 1px solid #A50F00;
		--list-border-radius: 0px;
		--font-size: 13.7px;
		--max-height: 30px;
		--item-is-active-color: #FFFFFF;
		--item-is-active-bg: #DA291C;
		--chevron-color: #DA291C;
		--item-hover-bg: #F8D4D2;
	}

	.des {
		margin-top: 4px;
		margin-left: 20px;
		margin-right: 20px;
		font-size: 14px;
		line-height: 18px;
	}

	#map {
		width: calc(100vw - 400px);
		height: 100vh;
		overflow: hidden;
		overflow-x: hidden;
	}

</style>
