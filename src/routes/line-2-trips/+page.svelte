<script>

	import "../../assets/global.css";
	import diagramImage from "./assets/ttc-line2-flow.png";
	import sofcLogo from "../../assets/top-logo-full.svg";

</script>

<svelte:head>

	<title>Arc diagram of Bloor-Danforth Subway (Line 2) trips | School of Cities</title>

	<meta name="description" content="Charting out AM peak trips in Toronto with R and data from the Transportation Tomorrow Survey.">
	<meta name="author" content="Jeff Allen">

	<meta property="og:title" content="Arc diagram of Bloor-Danforth Subway (Line 2) trips | School of Cities" />
	<meta property="og:description" content="Charting out AM peak trips in Toronto with R and data from the Transportation Tomorrow Survey." />
	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://schoolofcities.github.io/transportation-tomorrow-survey/line-2-trips/" />
	<meta property="og:image" content="https://raw.githubusercontent.com/schoolofcities/ggh-transport-geography/main/static/web-card-line2.png" />
	<meta property="og:locale" content="en_CA">

	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:site" content="https://schoolofcities.github.io/transportation-tomorrow-survey/line-2-trips/" />
	<meta name="twitter:creator" content="@JeffAllenMaps" />
	<meta name="twitter:title" content="Arc diagram of Bloor-Danforth Subway (Line 2) trips | School of Cities" />
	<meta name="twitter:description" content="Charting out AM peak trips in Toronto with R and data from the Transportation Tomorrow Survey." />
	<meta name="twitter:image" content="https://raw.githubusercontent.com/schoolofcities/ggh-transport-geography/main/static/web-card-line2.png" /> 

</svelte:head>

<main>

	<div class="arc-diagram">
		<a href={diagramImage} target="_blank">
			<img src={diagramImage} alt="Arc diagram of trips on the Bloor-Danforth Subway Line (Line 2) in Toronto during peak hours, showing connections between stations with arcs. The thickness and opacity of the arcs represent the number of trips between two stations." />
		</a>
		<p id="caption">Click on the image for a higher resolution</p>
	</div>

	<br><br>

	<div class="text">

		<h1>On creating this arc diagram of Line 2 morning peak trips</h1>

		<h3>~ <a href="https://jamaps.github.io/" target="_blank">Jeff Allen</a>, 2025</h3>

		<p>
			I used to ride the Bloor-Danforth Subway Line (Line 2) in Toronto a lot, especially when I lived in the east-end and commuted to/from downtown. Ride it a few times and you start to notice patterns in the way people board and alight at different stations, especially during peak hours - e.g. lots of people hopping on at Broadview, far fewer at Castle Frank, and so on.
		</p>

		<p>
			Thought that an arc diagram would be a fun way to visualize these patterns. 
		</p>

		<p>	
			An <a href="https://en.wikipedia.org/wiki/Arc_diagram" target="_blank">arc diagram</a> is a type of network visualization that shows connections between nodes (in this case, trips between subway stations) using arcs. The thickness and opacity of each arc represents the number of trips between two stations. Since people travel in two directions (eastbound and westbound), I divided the chart into two halves to show both components. 
		</p>

		<p>
			So where did the data come from?
		</p>

		<p>
			Ridership data stemming from Presto or credit card taps unfortunately wouldn't suffice. TTC is only tap on (boarding) but not tap off so we don't know where people end their trips. Moreover, many trips at the boarding station wouldn't be recorded anyway, since transfers from Line 1 or many surface transit routes do not require a tap. 
		</p>

		<p>
			Instead, I used data form the <a href="https://dmg.utoronto.ca/tts-introduction/" target="_blank">Transportation Tomorrow Survey</a> (TTS), which includes a questions about the subway line and station where people start and end their subway trips. The TTS is approximately a 5% sample, so while not comprehensive, it does provide a good overview of travel patterns.
		</p>

		<p>
			However, one issue with the TTS is that it only notes the start or end station, but not any transfer station. So for trips that start or end on other Lines (e.g. 1 or 4), I inferred the Line 2 leg based on the most likely transfer point. For example, if a trip started at Finch on Line 1 and ended at Bathurst, I assumed that it was most likely to transfer to Line 2 at Yonge-Bloor rather than looping down and around to St. George.
		</p>

		<p>
			All of this data processing as well as sketching of the chart was done in R (with ggplot). <a href="https://github.com/schoolofcities/transportation-tomorrow-survey/blob/main/src/routes/line-2-trips/assets/arc-diagram.R" target="_blank">Here is the R script</a>. I then exported it and added the labels and legend in <a href="https://inkscape.org/" target="_blank">Inkscape</a>, and adjusted the colours a bit in <a href="https://www.gimp.org/" target="_blank">GIMP</a>.
		</p>

		<p>
			That's it for now :) If you have any questions, comments, or suggestions, please feel free to reach out to me at <a>jeff.allen@utoronto.ca</a>
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

	.arc-diagram {
		margin: 0 auto;
		padding-top: 40px;
		max-width: 1000px;
		width: 100%;  
	}

	.arc-diagram img {
		width: 100%; 
		height: auto;
		display: block;
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