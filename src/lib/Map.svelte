<script>

	import { onMount } from "svelte";
	import maplibregl from "maplibre-gl";
	import "maplibre-gl/dist/maplibre-gl.css";
	import * as pmtiles from "pmtiles";
	import layers from 'protomaps-themes-base';
	import "../assets/global.css";
	import ttszones from "../data/tts2022.geo.json";
	import currentlines from "../data/CurrentTransitLines.geo.json";
	import futurelines from "../data/FutureTransitLines.geo.json";
	import Select from "svelte-select";

	let PMTILES_URL = 'https://api.protomaps.com/tiles/v4.json?key=7f48bb9c6a1f1e3b'

	let map = null;

	let colours = ["#f7ecc3", "#f2cd8d", "#eeb05b", "#e78052", "#e15449"];

	const defaultMap = "% of Households with No Vehicles";
	let mapSelected = defaultMap;

	const choropleths = {
		"Population Density": {
			dataSource: "Pop_Dens",
			breaks: [2000, 4000, 8000, 16000],
			colours: colours,
			text: "TTS Zone-level population density per sq km"
		},
		"% of Households with No Vehicles": {
			dataSource: "Perc_No_Veh",
			breaks: [6, 20, 40, 71],
			colours: colours,
			text: "Percentage of households in each TTS Zone that do not own a vehicle"
		}
	};

	const items = Object.keys(choropleths).map((key) => {
		return {
			label: key,
			value: key
		}
	});

	let mapLoaded = false
	
	function layerSelect(e) {
		if (!map || !mapLoaded) {
			console.warn("Map is not initialized or fully loaded yet.");
			return;
		}

		if (!map.isStyleLoaded()) {
			console.warn("Map style is not loaded yet. Waiting for style to load...");
			map.once('styledata', () => {
				layerSelect(e); // Retry after the style is loaded
			});
			return;
		}

		console.log("Setting layer:", e.detail.value);
		mapSelected = e.detail.value;
		layerSet(mapSelected);
	}		

	function layerSet(layer) {
		
		let choropleth = choropleths[layer];

		map.setPaintProperty("ttszones", "fill-opacity", 0.9);
		map.setPaintProperty("ttszones", "fill-color", [
			"case",
			["==", ["get", choropleth.dataSource], null], "#cbcbcb",
			["step", ["get", choropleth.dataSource],
			choropleth.colours[0], choropleth.breaks[0],
			choropleth.colours[1], choropleth.breaks[1],
			choropleth.colours[2], choropleth.breaks[2],
			choropleth.colours[3], choropleth.breaks[3],
			choropleth.colours[4]]			
		]);
		map.setPaintProperty("ttszones", "fill-outline-color", "#ffffff");
	}

	onMount(async () => {

		let protocol = new pmtiles.Protocol();
		maplibregl.addProtocol("pmtiles", protocol.tile);

		map = new maplibregl.Map({
			container: "map",
			style: {
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
				layers: layers("protomaps","light") // sub out for our own layer styles eventually
			},
			
			maxPitch: 0,
			maxZoom: 15,
			center: [-79.45, 43.75],
			zoom: 10

			// // variety of map interactivity/display settings to change later
			// projection: "globe",
			// scrollZoom: false,
			// dragPan: false,
			// dragRotate: false,
			// doubleClickZoom: false,
			// touchZoomRotate: false,
			// keyboard: false,
			// interactive: false,
			// attributionControl: false,

		});

		map.on('load', () => {

			map.addSource('ttszones', {
				type: 'geojson',
				data: ttszones
			});

			map.addSource('currentlines', {
				type: 'geojson',
				data: currentlines
			});

			map.addSource('futurelines', {
				type: 'geojson',
				data: futurelines
			});

			map.addLayer(
				{
					'id': 'ttszones',
					'type': 'fill',
					'source': 'ttszones',
					'paint': {
						'fill-color': [
							"case",
							["==", ["get", "Perc_No_Veh"], null], "#cbcbcb",
							["step", ["get", "Perc_No_Veh"],
							colours[0], 6,
							colours[1], 20,
							colours[2], 40,
							colours[3], 71,
							colours[4], 101,
							"#cbcbcb"]	
						],
						'fill-opacity': 1,
						'fill-outline-color': '#ffffff',
					}
				}
			);

			map.addLayer(
				{
					'id':'currentlines',
					'type':'line',
					'source':'currentlines',
					'paint': {
						'line-color': '#006400',
						'line-opacity': 0.95,
						'line-width': 2 
					}
				}
			)

			map.addLayer(
				{
					'id':'futurelines',
					'type':'line',
					'source':'futurelines',
					'paint': {
						'line-color': '#6C3BAA',
						'line-opacity': 0.95,
						'line-width': 2
					}
				}
			);

			mapLoaded = true;
			layerSelect({ detail: { value: mapSelected } });
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

		</div>

		<h3>Select Layers</h3>

		<div id='select-wrapper'>
			{#if map && mapLoaded}
				<Select
					id='select'
					items={items}
					value
					clearable={false}
					showChevron={true}
					listAutoWidth={true}
					searchable={false}
					listOffset = 10
					on:input={layerSelect}
				/>
			{/if}
		</div>

		<svg width='400' height={mapSelected == "% of Households with No Vehicles" ? 24 : 40}>
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

	</div>

	<div id="map"></div>

</div>


<style>

	#container {
		display: flex;
	}

	#panel {
		width: 400px;
		min-width: 400px;
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
		background-color: #89CFF0;
	}

	#title h1 {
		color: #000000;
	}

	#title h2 {
		color: #000000;
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

	#map {
		width: calc(100vw - 400px);
		height: 100vh;
		overflow: hidden;
		overflow-x: hidden;
	}

</style>
