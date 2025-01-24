<script>

	import { onMount } from "svelte";
	import maplibregl from "maplibre-gl";
	import "maplibre-gl/dist/maplibre-gl.css";
	import * as pmtiles from "pmtiles";
	import layers from 'protomaps-themes-base';
	import "../assets/global.css";

	let map;
	
	let PMTILES_URL = 'https://api.protomaps.com/tiles/v4.json?key=7f48bb9c6a1f1e3b'

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

		map.on("load", () => {

			console.log("hello world")

			// add in additional sources and layers in here when ready

		});
	
	});

</script>


<div id="map"></div>


<style>

	#map {
		width: 100vw;
		height: 100vh;
	}

</style>
