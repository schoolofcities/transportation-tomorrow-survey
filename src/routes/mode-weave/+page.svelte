<script>

	import "../../assets/global.css";
	import diagramImage from "./assets/mode-weave.png";
	import sofcLogo from "../../assets/top-logo-full.svg";

</script>

<svelte:head>

	<title>Mapping mode share in Toronto via weaving space | School of Cities</title>

	<meta name="description" content="Mapping percent of trips made by car, public transit, walking, and cycling in Toronto" />
	<meta name="author" content="Jeff Allen">

	<meta property="og:title" content="Mapping mode share in Toronto via weaving space | School of Cities" />
	<meta property="og:description" content="Mapping percent of trips made by car, public transit, walking, and cycling in Toronto" />
	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://schoolofcities.github.io/transportation-tomorrow-survey/mode-weave/" />
	<meta property="og:image" content="https://raw.githubusercontent.com/schoolofcities/ggh-transport-geography/main/static/web-card-modeweave.png" />
	<meta property="og:locale" content="en_CA">

	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:site" content="https://schoolofcities.github.io/transportation-tomorrow-survey/mode-weave/" />
	<meta name="twitter:creator" content="@JeffAllenMaps" />
	<meta name="twitter:title" content="Mapping mode share in Toronto via weaving space | School of Cities" />
	<meta name="twitter:description" content="Mapping percent of trips made by car, public transit, walking, and cycling in Toronto" />
	<meta name="twitter:image" content="https://raw.githubusercontent.com/schoolofcities/ggh-transport-geography/main/static/web-card-modeweave.png" /> 

</svelte:head>

<main>

	<div class="mode-weave">
		<a href={diagramImage} target="_blank">
			<img src={diagramImage} alt="Arc diagram of trips on the Bloor-Danforth Subway Line (Line 2) in Toronto during peak hours, showing connections between stations with arcs. The thickness and opacity of the arcs represent the number of trips between two stations." />
		</a>
		<p id="caption">Click on the image for a higher resolution</p>
	</div>

	<br><br>

	<div class="text">

		<h1>Mapping mode share in Toronto via weaving space</h1>

		<h3>~ <a href="https://jamaps.github.io/" target="_blank">Jeff Allen</a>, 2025</h3>

		<p>
			
		</p>

		<p>
			A couple months ago we built an <a href="https://schoolofcities.github.io/transportation-tomorrow-survey/" target="_blank">interactive map</a> for viewing <a href="https://dmg.utoronto.ca/tts-introduction/" target="_blank">Transportation Tomorrow Survey</a> (TTS) data. 
			Among the several layers on the map are maps of travel mode share: what percentage of trips are made by car, public transit, walking, and cycling. These maps are useful for understanding how people travel in the region, but they only show one mode at a time and so can be hard to compare, especially if you want to compare four at once!
		</p>

		<p>
			<a href="https://schoolofcities.github.io/urban-data-storytelling/urban-data-visualization/bivariate-choropleth-maps/bivariate-choropleth-maps.html" target="_blank">Bivariate maps</a> are a relatively common option for mapping two variables at once, and showing correlations. There are also <a href="https://censusmapper.ca/maps/3720" target="_blank">trivariate</a> options. But what about four or more? 
		</p>
		<p>	
			At the recent 2025 Canadian Cartographic Association conference there was a great presentation by Luke Bergmann on <a href="https://github.com/DOSull/weaving-space" target="_blank">weavingspace</a>, a Python library developed by him and David O'Sullivan that can visualize multiple variables in a single map by weaving them together with a variety of pattern options. I thought this library would be a fun exploratory way to try to visualize multi-variate travel mode share on a single map.
		</p>
		<p>
			The benefit of this approach is that it allows for the simultaneous visualization of multiple variables, making it easier to compare and contrast them, both at a zoomed-out city wide scale as well as at a zoomed-in neighbourhood scale. The four individual maps below the main map are great for regional scale comparisons, but are more difficult to compare at a neighbourhood scale. The weaving space approach allows for both of these scales to be compared at once, and the patterns can be used to show the relative share of each mode in a given area.
		</p>
		<p>
			Moreover, by having a flat white colour as the lowest category of each of the four scales simultaneously allows for showing areas that are quite multi-modal (e.g. neighbourhoods just east and west of downtown where we see less white space means that all four modes are used regularly) or where one mode is dominant (e.g. in western Etobicoke and eastern Scarborough, where car travel is by far the most dominant mode).
		</p>
		<p>
			There are some drawbacks though. By being quite data-dense, the map takes longer to read and parse out patterns than maps with fewer variables. The arbitrary selection of the tile size, shape, and placement could also be showing specific results (i.e. due to <a href="https://en.wikipedia.org/wiki/Modifiable_areal_unit_problem" target="_blank">MAUP</a>) compared to other selection options. In terms of the data, the TTS is approximately a 5% sample, so while it does provide a good overview of travel patterns, small samples in some areas could cause misleading results. The map does have a mask over it (in a gray hatch pattern) to cover non-residential areas or tiles with low sample sizes.
		</p>
		<p>
			That's it for now! If you have any questions, comments, or suggestions, please feel free to reach out to me at <a>jeff.allen@utoronto.ca</a>
		</p>

	</div>

	<br>

	<a href="https://schoolofcities.utoronto.ca/" target="_blank">
		<img 
			src={sofcLogo} 
			alt="School of Cities logo" 
			style="display: block; margin: 0 auto; width: 300px; height: auto; opacity: 1"
			on:mouseover={() => (event.target.style.opacity = 0.8)}
			on:mouseout={() => (event.target.style.opacity = 1)}
		/>
	</a>

	<br><br><br>

</main>



<style>

	main {
		background-color: #fefefe;
	}

	.mode-weave {
		margin: 0 auto;
		padding-top: 20px;
		max-width: calc(1080px + 540px);
		width: 100%;  
		
	}

	.mode-weave img {
		width: 100%; 
		height: auto;
		display: block;
		border: solid 1px #f5f5f5;
	}

	#caption{
		font-size: 12px;
		margin-top: 2px;
		padding-left: 1px;
		color: #8a8a8a;
	}

	a {
		color: var(--brandBlack);
		text-decoration: underline
	}

	a:hover {
		color: var(--brandDarkBlue);
	}

</style>