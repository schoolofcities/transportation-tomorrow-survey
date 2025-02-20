<script>

	import { onMount } from "svelte";
	import maplibregl from "maplibre-gl";
	import "maplibre-gl/dist/maplibre-gl.css";
	import * as pmtiles from "pmtiles";
	import layers from 'protomaps-themes-base';
	import "../assets/global.css";
	import ttszones from "../data/tts2022zones.geo.json";
	import currentlines from "../data/CurrentTransitLines.geo.json";
	import futurelines from "../data/FutureTransitLines.geo.json";

	let map;
	
	let PMTILES_URL = 'https://api.protomaps.com/tiles/v4.json?key=7f48bb9c6a1f1e3b'

	let colours = ["#f7ecc3", "#f2cd8d", "#eeb05b", "#e78052", "#e15449"];

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
							'step', ['get', 'Perc_No_Veh'],
							colours[0], 0.2,
							colours[1], 0.4,
							colours[2], 0.6,
							colours[3], 0.8,
							colours[4], 1.01,
							'#cbcbcb'
						],
						'fill-opacity': 0.5,
						'fill-outline-color': '#000000'
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
						'line-width': 2,
						'line-dasharray': [1.5, 1.5] 
					}
				}
			);
		});

		const popup = new maplibregl.Popup({
			closeButton: false,     // The idea is to make the popup close when the mouse leaves. So no close button shld be present on the popup
			closeOnClick: false     // The idea is to make the popup close when the mouse leaves. So no clicking of mouse is required
		});

		// Initialising the mouseenter event to popup 
		map.on('mouseenter', 'ttszones', (e) => {
			map.getCanvas().style.cursor = 'pointer';                       // Changing the cursor to a pointer when the mouse hovers on the restaurant

    		const coordinates = e.lngLat; 								// Getting the coordinates of the restaurant that the mouse is hovering on
    		const description = e.features[0].properties.TTS2022 + '<br>' + e.features[0].properties.Perc_No_Veh;	// Setting description to be the percentage of hh with no vehicles

   			popup
			 .setLngLat(coordinates)                                     // Setting the popup to be located on the coordinates of the restaurant
			 .setHTML(description)                                       // Setting the description in the popup
			 .addTo(map);                                                // Adding the popup to the map
		});

		// Initialising the mouseleave event to remove the popup
		map.on('mouseleave', 'ttszones', () => {
			map.getCanvas().style.cursor = '';                              // Changing the cursor back to default when the mouse hovers away from the restaurant
    		popup.remove();                                                 // Removing the popup from the map
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

	</div>

	<div id="map"></div>

</div>


<style>

	#map {
		width: 100vw;
		height: 100vh;
	}

</style>
