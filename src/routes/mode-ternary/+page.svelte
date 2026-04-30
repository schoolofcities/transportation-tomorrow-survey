<script>
	import { onMount } from 'svelte';
	import csvTransit from './assets/modes_percent_transit_line.csv?raw';
	import csvStations from './assets/modes_percent_station.csv?raw';
	import csvMunicipality from './assets/modes_percent_municipality.csv?raw';
	import csvIncome from './assets/modes_percent_income.csv?raw';
	import csvImmigration from './assets/modes_percent_immigration.csv?raw';
	import csvAge from './assets/modes_percent_age.csv?raw';
	import csvAgeGender from './assets/modes_percent_age_gender.csv?raw';
	import * as d3 from 'd3';
	import '../../assets/global.css';
	import sofcLogo from "../../assets/top-logo-full.svg";

	let rows = [];

	// ===== EDITABLE PARAMETERS (Top of file) =====
	// Change these constants to adjust labels, sizes, and colours used in the chart
	// Triangular background gradient colours (editable)
	const DRIVE_COLOUR = '#DC4633';
	const TRANSIT_COLOUR = '#007FA3';
	const ACTIVE_COLOUR = '#8DBF2E';
	const TRI_GRAD_OPACITY = 0.05;

	// Chart title and subtitle (editable)
	const CHART_TITLE = 'How does Toronto travel?';
	const CHART_SUBTITLE = 'Exploring patterns of daily travel mode share via ternary charts'
	let chartSubtext = '';
	const dataSource = 'Data source: Transportation Tomorrow Survey, 2022-23';
	const authorText = 'Jeff Allen, Polina Gorn';
	const dateText = 'April 2026';

	// Dataset registry (JSON): add entries for each CSV here
	const DATASETS = [
		{
			id: 'age',
			fileName: 'modes_percent_age.csv',
			title: 'Age',
			infoText: 'Mode share by City of Toronto residents grouped by age.',
			raw: csvAge
		},
		{
			id: 'age_gender',
			fileName: 'modes_percent_age_gender.csv',
			title: 'Age and gender',
			infoText: 'Mode share by City of Toronto residents grouped by age and gender.',
			raw: csvAgeGender
		},
		{
			id: 'income',
			fileName: 'modes_percent_income.csv',
			title: 'Household income',
			infoText: 'Mode share by City of Toronto residents grouped by their household income.',
			raw: csvIncome
		},
		{
			id: 'immigration',
			fileName: 'modes_percent_immigration.csv',
			title: 'Immigration',
			infoText: 'Mode share by City of Toronto residents grouped by if and when they immigrated to Canada.',
			raw: csvImmigration
		},
		{
			id: 'upper_tier_municipalities',
			fileName: 'modes_percent_upper_tier_municipality.csv',
			title: 'Municipality',
			infoText: 'Mode share by residents in Toronto compared to municipalities in the Greater Golden Horseshoe',
			raw: csvMunicipality
		},
		{
			id: 'transit_lines',
			fileName: 'modes_percent_transit_line.csv',
			title: 'Near major transit lines',
			infoText: 'Mode share of residents who live within 800m of stations on major transit lines',
			raw: csvTransit
		},
		{
			id: 'transit_stations',
			fileName: 'modes_percent_station.csv',
			title: 'Near major transit stations',
			infoText: 'Mode share of residents who live within 800m of stations on major transit lines (in operation by the time of the survey)',
			raw: csvStations
		}
	];

	let selectedDataset = DATASETS[4].id;
	// ===== End editable parameters =====

	// Chart dimensions
	const triW = 680;
	const hRatio = Math.sqrt(3) / 2;
	const triH = hRatio * triW;
	const margin = 95;
	const svgW = triW + margin * 2;
	const svgH = triH + margin * 2;

	// Left / right boxes inside the triangle bounding box
	const sideBoxPadding = -50;
	const leftBoxWidth = Math.min(280, Math.floor(triW / 2 - 24));
	const rightBoxWidth = 250;
	const leftBoxX = margin + sideBoxPadding;
	const leftBoxY = margin + sideBoxPadding - 5;
	const rightBoxX = margin + triW - rightBoxWidth - sideBoxPadding;
	const rightBoxY = margin + sideBoxPadding;

	// Grid and data point styling
	const gridFractions = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1];
	const majorGridFractions = [0.5];
	const circleBase = 6;
	const circleHover = 8;
	const squareBase = 12;
	const squareHover = 16;

	const tickLen = 12;
	const LINE_GROUP_STROKE_WIDTH = 1.5;
	const LINE_GROUP_OPACITY = 0.65;

	// Axis and callout labels
	const AXIS_LABEL_ACTIVE = 'trips by active modes (walking or bicycle) (%)';
	const AXIS_LABEL_DRIVE = 'trips by motor vehicle (%)';
	const AXIS_LABEL_TRANSIT = 'trips by public transit (%)';

	const CALLOUT_EVERYBODY = 'Everybody';
	const CALLOUT_DRIVE = 'drives';
	const CALLOUT_TRANSIT = 'takes transit';
	const CALLOUT_ACTIVE = 'walks or bikes';

	// precompute grid lines for three axes
	const activeGrid = gridFractions.map((f) => ({
		x1: margin + 0.5 * f * triW,
		y1: margin + triH * (1 - f),
		x2: margin + (1 - 0.5 * f) * triW,
		y2: margin + triH * (1 - f)
	}));

	const driveGrid = gridFractions.map((f) => ({
		x1: margin + 0.5 * (1 - f) * triW,
		y1: margin + triH * f,
		x2: margin + (1 - f) * triW,
		y2: margin + triH
	}));

	const transitGrid = gridFractions.map((f) => ({
		x1: margin + triW * f,
		y1: margin + triH,
		x2: margin + 0.5 * (1 + f) * triW,
		y2: margin + triH * f
	}));

	const majorActiveGrid = majorGridFractions.map((f) => ({
		x1: margin + 0.5 * f * triW,
		y1: margin + triH * (1 - f),
		x2: margin + (1 - 0.5 * f) * triW,
		y2: margin + triH * (1 - f)
	}));

	const majorDriveGrid = majorGridFractions.map((f) => ({
		x1: margin + 0.5 * (1 - f) * triW,
		y1: margin + triH * f,
		x2: margin + (1 - f) * triW,
		y2: margin + triH
	}));

	const majorTransitGrid = majorGridFractions.map((f) => ({
		x1: margin + triW * f,
		y1: margin + triH,
		x2: margin + 0.5 * (1 + f) * triW,
		y2: margin + triH * f
	}));

	// Compute tick marks for each axis at the intersection point on the corresponding triangle side
	$: activeTicks = gridFractions.map((f, i) => {
		const g = activeGrid[i];
		const cx = g.x2;
		const cy = g.y2;
		let dx = g.x2 - g.x1;
		let dy = g.y2 - g.y1;
		// For f=1 (100%), grid line collapses to a point; use horizontal direction (all activeGrid lines are horizontal)
		if (f === 1) {
			dx = 1;
			dy = 0;
		}
		const L = Math.hypot(dx, dy) || 1;
		const nx = dx / L;
		const ny = dy / L;
		let angle = (Math.atan2(ny, nx) * 180) / Math.PI;
		if (angle > 90) angle -= 180;
		if (angle < -90) angle += 180;
		return {
			x1: cx - nx * (tickLen / 2),
			y1: cy - ny * (tickLen / 2),
			x2: cx + nx * (tickLen / 2),
			y2: cy + ny * (tickLen / 2),
			tx: cx + 8,
			ty: cy + 4,
			anchor: 'start',
			angle,
			val: Math.round(f * 100)
		};
	});

	$: driveTicks = gridFractions.map((f, i) => {
		const g = driveGrid[i];
		const cx = g.x1;
		const cy = g.y1;
		let dx = g.x2 - g.x1;
		let dy = g.y2 - g.y1;
		// For f=1 (100%), grid line collapses to a point; use limiting direction of driveGrid
		if (f === 1) {
			dx = 0.5 * triW;
			dy = triH;
		}
		const L = Math.hypot(dx, dy) || 1;
		const nx = dx / L;
		const ny = dy / L;
		let angle = (Math.atan2(ny, nx) * 180) / Math.PI;
		if (angle > 90) angle -= 180;
		if (angle < -90) angle += 180;
		return {
			x1: cx - nx * (tickLen / 2),
			y1: cy - ny * (tickLen / 2),
			x2: cx + nx * (tickLen / 2),
			y2: cy + ny * (tickLen / 2),
			tx: cx - 4,
			ty: cy - 8,
			anchor: 'end',
			angle,
			val: Math.round(f * 100)
		};
	});

	$: transitTicks = gridFractions.map((f, i) => {
		const g = transitGrid[i];
		const cx = g.x1;
		const cy = g.y1;
		let dx = g.x2 - g.x1;
		let dy = g.y2 - g.y1;
		// For f=1 (100%), grid line collapses to a point; use limiting direction of transitGrid
		if (f === 1) {
			dx = 0.5 * triW;
			dy = -triH;
		}
		const L = Math.hypot(dx, dy) || 1;
		const nx = dx / L;
		const ny = dy / L;
		let angle = (Math.atan2(ny, nx) * 180) / Math.PI;
		if (angle > 90) angle -= 180;
		if (angle < -90) angle += 180;
		return {
			x1: cx - nx * (tickLen / 2),
			y1: cy - ny * (tickLen / 2),
			x2: cx + nx * (tickLen / 2),
			y2: cy + ny * (tickLen / 2),
			tx: cx - 4,
			ty: cy + 16,
			anchor: 'middle',
			angle,
			val: Math.round(f * 100)
		};
	});

	// Hover guide lines (follow cursor)
	let hoverGuide = { show: false, lx: 0, ly: 0, activeF: 0, transitF: 0, driveF: 0 };
	let hoverActiveLine = null;
	let hoverDriveLine = null;
	let hoverTransitLine = null;

	function intersectLineWithSegment(px, py, ux, uy, ax, ay, bx, by) {
		const vx = bx - ax;
		const vy = by - ay;
		const rx = ax - px;
		const ry = ay - py;
		const D = vx * uy - ux * vy;
		if (Math.abs(D) < 1e-8) return null;
		const t = (-rx * vy + vx * ry) / D;
		const s = (ux * ry - uy * rx) / D;
		if (s < -1e-6 || s > 1 + 1e-6) return null;
		const ix = ax + s * vx;
		const iy = ay + s * vy;
		return { ix, iy, t, s };
	}

	function pointInTriangle(px, py, ax, ay, bx, by, cx, cy) {
		function sign(x1, y1, x2, y2, x3, y3) {
			return (x1 - x3) * (y2 - y3) - (x2 - x3) * (y1 - y3);
		}
		const d1 = sign(px, py, ax, ay, bx, by);
		const d2 = sign(px, py, bx, by, cx, cy);
		const d3 = sign(px, py, cx, cy, ax, ay);
		const hasNeg = d1 < 0 || d2 < 0 || d3 < 0;
		const hasPos = d1 > 0 || d2 > 0 || d3 > 0;
		return !(hasNeg && hasPos);
	}

	function handleSvgPointerMove(e) {
		const svg = e.currentTarget;
		const rect = svg.getBoundingClientRect();
		const clientX = e.touches ? e.touches[0].clientX : e.clientX;
		const clientY = e.touches ? e.touches[0].clientY : e.clientY;
		const scale = svgW / rect.width;
		const lx = (clientX - rect.left) * scale;
		const ly = (clientY - rect.top) * scale;

		const activeF = 1 - (ly - margin) / triH;
		const transitF = (lx - margin - 0.5 * triW * activeF) / triW;
		const driveF = 1 - transitF - activeF;

		const af = Math.max(0, Math.min(1, activeF));
		const tf = Math.max(0, Math.min(1, transitF));
		const df = Math.max(0, Math.min(1, driveF));

		// triangle side endpoints
		const top = { x: margin + triW / 2, y: margin };
		const leftB = { x: margin, y: margin + triH };
		const rightB = { x: margin + triW, y: margin + triH };

		// only show hover guides when cursor is inside the triangle
		if (!pointInTriangle(lx, ly, top.x, top.y, leftB.x, leftB.y, rightB.x, rightB.y)) {
			hideHoverGuide();
			return;
		}

		// compute grid direction unit vectors (use first grid line as representative)
		const gA = activeGrid[0];
		const gD = driveGrid[0];
		const gT = transitGrid[0];
		const uA = (() => { const dx = gA.x2 - gA.x1; const dy = gA.y2 - gA.y1; const L = Math.hypot(dx, dy)||1; return {x: dx / L, y: dy / L}; })();
		const uD = (() => { const dx = gD.x2 - gD.x1; const dy = gD.y2 - gD.y1; const L = Math.hypot(dx, dy)||1; return {x: dx / L, y: dy / L}; })();
		const uT = (() => { const dx = gT.x2 - gT.x1; const dy = gT.y2 - gT.y1; const L = Math.hypot(dx, dy)||1; return {x: dx / L, y: dy / L}; })();

		// sides to intersect with (these correspond to where ticks/labels are placed)
		const sideActiveA = top; const sideActiveB = rightB; // right side
		const sideDriveA = leftB; const sideDriveB = top; // left side
		const sideTransitA = leftB; const sideTransitB = rightB; // bottom side

		const ia = intersectLineWithSegment(lx, ly, uA.x, uA.y, sideActiveA.x, sideActiveA.y, sideActiveB.x, sideActiveB.y);
		const id = intersectLineWithSegment(lx, ly, uD.x, uD.y, sideDriveA.x, sideDriveA.y, sideDriveB.x, sideDriveB.y);
		const it = intersectLineWithSegment(lx, ly, uT.x, uT.y, sideTransitA.x, sideTransitA.y, sideTransitB.x, sideTransitB.y);

		hoverGuide = { show: true, lx, ly, activeF: af, transitF: tf, driveF: df };
		hoverActiveLine = ia ? { x1: lx, y1: ly, x2: ia.ix, y2: ia.iy } : { x1: lx, y1: ly, x2: lx, y2: ly };
		hoverDriveLine = id ? { x1: lx, y1: ly, x2: id.ix, y2: id.iy } : { x1: lx, y1: ly, x2: lx, y2: ly };
		hoverTransitLine = it ? { x1: lx, y1: ly, x2: it.ix, y2: it.iy } : { x1: lx, y1: ly, x2: lx, y2: ly };
	}

	function hideHoverGuide() {
		hoverGuide.show = false;
		hoverActiveLine = null;
		hoverDriveLine = null;
		hoverTransitLine = null;
	}

	let wrapEl;
	let tooltip = { show: false, x: 0, y: 0, row: null };
	let hoveredRow = null;
	let dropdownOpen = false;

	// area polygons (convex hull per Area) — reactive to `rows`
	$: areaPolygons = (() => {
		if (!rows || rows.length === 0) return [];
		const groups = d3.group(rows, (r) => r.area);
		const polys = [];
		for (const [area, members] of groups) {
			if (!area) continue;
			const pts = members.map((m) => [m.x, m.y]);
			if (pts.length < 3) continue;
			const hull = d3.polygonHull(pts);
			if (!hull) continue;
			const fill = (members[0].areaFill || members[0].AreaFill || '#cccccc').trim();
			polys.push({ area, hull, fill });
		}
		return polys;
	})();

	$: lineConnections = (() => {
		if (!rows || rows.length === 0) return [];
		const groups = new Map();
		for (const row of rows) {
			if (!row.line) continue;
			if (!groups.has(row.line)) groups.set(row.line, []);
			groups.get(row.line).push(row);
		}
		return Array.from(groups.values()).filter((members) => members.length > 1);
	})();

	function handlePointer(e, row) {
		const rect = wrapEl.getBoundingClientRect();
		const clientX = e.touches ? e.touches[0].clientX : e.clientX;
		const clientY = e.touches ? e.touches[0].clientY : e.clientY;
		tooltip.x = clientX - rect.left + 12;
		tooltip.y = clientY - rect.top + 12;
		tooltip.row = row;
		tooltip.show = true;
		hoveredRow = row;
	}

	function hideTooltip() {
		tooltip.show = false;
		tooltip.row = null;
		hoveredRow = null;
	}


	function parseCsvText(csvRaw) {
		const parsed = d3.csvParse(csvRaw || '');
		const cols = parsed.columns || (parsed.length ? Object.keys(parsed[0]) : []);
		const sizeCol = cols.find((c) => c && c.toLowerCase() === 'symbolsize');
		rows = parsed.map((r, i) => {
			const walk = +r.walk_percent || 0;
			const bike = +r.bike_percent || 0;
			const transit = +r.transit_percent || 0;
			const drive = +r.drive_percent || 0;
			const active = walk + bike;
			const sum = drive + transit + active || 1;
			const driveF = drive / sum;
			const transitF = transit / sum;
			const activeF = active / sum;
			// barycentric -> Cartesian
			const x = margin + triW * (transitF + 0.5 * activeF);
			const y = margin + triH * (1 - activeF);
			const name = r.Name || r.NAME || r.name || '';
			const short = name;
			const lineTag = (r.line || r.Line || r.LINE || '').toString().trim();
			const lineStrokeColour = (r.strokeColour || r.StrokeColour || r.strokecolour || r.Strokecolour || r.strokeColor || r.StrokeColor || r.strokecolour || '').trim();
			const stroke = (r.Stroke || r.stroke || '#000').trim();
			const fill = (r.Fill || r.fill || 'none').trim();
			const symbol = (r.Symbol || r.symbol || 'circle').toString();
			const symbolSizeRaw = sizeCol ? r[sizeCol] : (r.SymbolSize || r.symbolSize || r.symbolsize || r.symbol_size);
			const symbolSize = symbolSizeRaw ? +symbolSizeRaw : null;
			const area = (r.Area || r.area || '').toString();
			const areaFill = (r.AreaFill || r.areaFill || '').toString();
			const label = (r.Label || r.label || '').toString();
			const baseSize = symbolSize || (symbol.toLowerCase().includes('square') ? squareBase : circleBase);
			const hoverSize = baseSize + 2;
			return {
				original: r,
				name,
				short,
				line: lineTag,
				lineStrokeColour,
				walk,
				bike,
				transit,
				drive,
				active,
				driveF,
				transitF,
				activeF,
				x,
				y,
				stroke,
				fill,
				symbol,
				area,
				areaFill,
				label,
				symbolSize,
				pointSize: baseSize,
				hoverPointSize: hoverSize
			};
		});
	}

	function handleDatasetSelect(id) {
		const ds = DATASETS.find(d => d.id === id);
		if (!ds) return;
		chartSubtext = ds.infoText || '';
		parseCsvText(ds.raw || '');
	}

	onMount(() => {
		handleDatasetSelect(selectedDataset);
	});
</script>







<svelte:head>

	<title>Charting mode share in Toronto via ternary charts | School of Cities</title>

	<meta name="description" content="Visualizing percent of trips made by car, public transit, and active travel in the Toronto region" />
	<meta name="author" content="Jeff Allen">

	<meta property="og:title" content="Charting mode share in Toronto via ternary charts | School of Cities" />
	<meta property="og:description" content="Visualizing percent of trips made by car, public transit, and active travel in the Toronto region" />
	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://schoolofcities.github.io/transportation-tomorrow-survey/mode-ternary/" />
	<meta property="og:image" content="https://raw.githubusercontent.com/schoolofcities/ggh-transport-geography/main/static/web-card-ternary.png" />
	<meta property="og:locale" content="en_CA">

	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:site" content="https://schoolofcities.github.io/transportation-tomorrow-survey/mode-ternary/" />
	<meta name="twitter:creator" content="@JeffAllenMaps" />
	<meta name="twitter:title" content="Charting mode share in Toronto via ternary charts | School of Cities" />
	<meta name="twitter:description" content="Visualizing percent of trips made by car, public transit, and active travel in the Toronto region" />
	<meta name="twitter:image" content="https://raw.githubusercontent.com/schoolofcities/ggh-transport-geography/main/static/web-card-ternary.png" /> 

</svelte:head>





<svelte:window on:click={() => { dropdownOpen = false; }} />

<div class="chart-space">

<div class="chart-wrap" bind:this={wrapEl}>
	<svg width="100%" style="max-width: {svgW}px" viewBox={`0 0 ${svgW} ${svgH}`} aria-label="Ternary mode share chart" overflow="visible" on:mousemove={handleSvgPointerMove} on:mouseleave={hideHoverGuide}>
		<!-- Bounding box for the svg area -->
		<rect x="0" y="0" width={svgW} height={svgH} fill="none" stroke="#ddd" stroke-width="1" />

		<!-- Left info box (top-left whitespace inside triangle bounding box) -->
		<foreignObject x={leftBoxX} y={leftBoxY} width={leftBoxWidth} height="240">
			<div xmlns="http://www.w3.org/1999/xhtml" class="fo-left">
				<h1 class="chart-heading">{CHART_TITLE}</h1>
				<h2 class="chart-subheading">{CHART_SUBTITLE}</h2>
				<div class="fo-author">{authorText}</div>
				<div class="fo-date">{dateText}</div>
			</div>
		</foreignObject>

		<!-- Right info box (top-right whitespace) -->
		<foreignObject x={rightBoxX} y={rightBoxY} width={rightBoxWidth} height="300" overflow="visible">
			<div xmlns="http://www.w3.org/1999/xhtml" class="fo-right" style="text-align:right;">
				<div class="custom-dropdown" role="none" on:click|stopPropagation on:keydown|stopPropagation>
					<button type="button" class="dropdown-trigger" on:click={() => dropdownOpen = !dropdownOpen}>
						<span class="dropdown-chevron">▾</span>
						<span class="dropdown-label">{DATASETS.find(d => d.id === selectedDataset)?.title}</span>
					</button>
					{#if dropdownOpen}
						<div class="dropdown-list" role="listbox">
							{#each DATASETS as ds}
								<button
									type="button"
									role="option"
									aria-selected={ds.id === selectedDataset}
									class:active={ds.id === selectedDataset}
									on:click={() => { selectedDataset = ds.id; handleDatasetSelect(ds.id); dropdownOpen = false; }}
								>{ds.title}</button>
							{/each}
						</div>
					{/if}
				</div>
				<div class="svg-subtext">{chartSubtext}</div>
				<div class="fo-data-source">{dataSource}</div>
				<div class="fo-instructions">Click on or hover over each point to display specific stats</div>
			</div>
		</foreignObject>

		<!-- Triangle outline -->
		<polygon
			points={`${margin},${margin + triH} ${margin + triW},${margin + triH} ${margin + triW / 2},${margin}`}
			fill="none"
			stroke="#333"
			stroke-width="0.5"
		/>

		<defs>
			<clipPath id="triClip">
				<polygon points={`${margin},${margin + triH} ${margin + triW},${margin + triH} ${margin + triW / 2},${margin}`} />
			</clipPath>
			<radialGradient id="gDrive" gradientUnits="userSpaceOnUse" cx={margin} cy={margin + triH} r={triW}>
				<stop offset="0%" stop-color={DRIVE_COLOUR} stop-opacity={TRI_GRAD_OPACITY} />
				<stop offset="100%" stop-color={DRIVE_COLOUR} stop-opacity="0" />
			</radialGradient>
			<radialGradient id="gTransit" gradientUnits="userSpaceOnUse" cx={margin + triW} cy={margin + triH} r={triW}>
				<stop offset="0%" stop-color={TRANSIT_COLOUR} stop-opacity={TRI_GRAD_OPACITY} />
				<stop offset="100%" stop-color={TRANSIT_COLOUR} stop-opacity="0" />
			</radialGradient>
			<radialGradient id="gActive" gradientUnits="userSpaceOnUse" cx={margin + triW/2} cy={margin} r={triW}>
				<stop offset="0%" stop-color={ACTIVE_COLOUR} stop-opacity={TRI_GRAD_OPACITY} />
				<stop offset="100%" stop-color={ACTIVE_COLOUR} stop-opacity="0" />
			</radialGradient>
		</defs>

		<g clip-path="url(#triClip)" style="mix-blend-mode: screen;">
			<circle cx={margin} cy={margin + triH} r={triW} fill="url(#gDrive)" />
			<circle cx={margin + triW} cy={margin + triH} r={triW} fill="url(#gTransit)" />
			<circle cx={margin + triW/2} cy={margin} r={triW} fill="url(#gActive)" />
		</g>

		<!-- Grid lines: active, drive, transit -->
		{#each activeGrid as g}
			<line class="grid-line" x1={g.x1} y1={g.y1} x2={g.x2} y2={g.y2} />
		{/each}
		{#each driveGrid as g}
			<line class="grid-line" x1={g.x1} y1={g.y1} x2={g.x2} y2={g.y2} />
		{/each}
		{#each transitGrid as g}
			<line class="grid-line" x1={g.x1} y1={g.y1} x2={g.x2} y2={g.y2} />
		{/each}

		<!-- Major grid lines (e.g. 50%) -->
		{#each majorActiveGrid as g}
			<line class="grid-major" x1={g.x1} y1={g.y1} x2={g.x2} y2={g.y2} />
		{/each}
		{#each majorDriveGrid as g}
			<line class="grid-major" x1={g.x1} y1={g.y1} x2={g.x2} y2={g.y2} />
		{/each}
		{#each majorTransitGrid as g}
			<line class="grid-major" x1={g.x1} y1={g.y1} x2={g.x2} y2={g.y2} />
		{/each}

		<!-- Area polygons (above grid, behind points) -->
		{#each areaPolygons as poly}
			<polygon points={poly.hull.map(p => p.join(',')).join(' ')} fill={poly.fill} fill-opacity="0.35" stroke="none" class="area-polygon" />
		{/each}

		<!-- Line connections for points sharing the same line tag -->
		{#each lineConnections as members}
			{#each members as point, idx}
				{#if idx > 0}
					<line
						class="line-connector"
						x1={members[idx - 1].x}
						y1={members[idx - 1].y}
						x2={point.x}
						y2={point.y}
						stroke={point.lineStrokeColour || members[idx - 1].stroke || '#777'}
						stroke-width={LINE_GROUP_STROKE_WIDTH}
						opacity={LINE_GROUP_OPACITY}
					/>
				{/if}
			{/each}
		{/each}

		{#if hoverGuide.show}
			<line class="hover-grid-line" x1={hoverActiveLine.x1} y1={hoverActiveLine.y1} x2={hoverActiveLine.x2} y2={hoverActiveLine.y2} />
			<line class="hover-grid-line" x1={hoverDriveLine.x1} y1={hoverDriveLine.y1} x2={hoverDriveLine.x2} y2={hoverDriveLine.y2} />
			<line class="hover-grid-line" x1={hoverTransitLine.x1} y1={hoverTransitLine.y1} x2={hoverTransitLine.x2} y2={hoverTransitLine.y2} />
		{/if}

		<!-- Ticks (one chosen side per axis) -->
		{#each activeTicks as t}
			<line class="tick-line" x1={t.x1} y1={t.y1} x2={t.x2} y2={t.y2} />
			<text class="tick-label" x={t.tx} y={t.ty} text-anchor={t.anchor}>{t.val}%</text>
		{/each}
		{#each driveTicks as t}
			<line class="tick-line" x1={t.x1} y1={t.y1} x2={t.x2} y2={t.y2} />
			<text class="tick-label" x={t.tx} y={t.ty} text-anchor={t.anchor}>{t.val}%</text>
		{/each}
		{#each transitTicks as t}
			<line class="tick-line" x1={t.x1} y1={t.y1} x2={t.x2} y2={t.y2} />
			<text class="tick-label" x={t.tx} y={t.ty} text-anchor={t.anchor}>{t.val}%</text>
		{/each}

		<!-- Axis titles (placed on the side requested, bumped outward) -->
		<text class="axis-title" transform={`translate(${margin + triW/2}, ${margin + triH + 40}) rotate(0)`} text-anchor="middle">{AXIS_LABEL_TRANSIT}</text>
		<text class="axis-title" transform={`translate(${margin + triW * 0.75 + 42}, ${margin + triH/2}) rotate(60)`} text-anchor="middle">{AXIS_LABEL_ACTIVE}</text>
		<text class="axis-title" transform={`translate(${margin + triW * 0.25 - 42}, ${margin + triH/2}) rotate(-60)`} text-anchor="middle">{AXIS_LABEL_DRIVE}</text>

		<!-- Callout labels for extremes (line-break after 'Everybody' and placed outside triangle) -->
		<text class="callout-label" x={margin - 12} y={margin + triH + 16} text-anchor="end">
			<tspan x={margin - 1} dy="0">{CALLOUT_EVERYBODY}</tspan>
			<tspan x={margin - 4} dy="1.05em">{CALLOUT_DRIVE}</tspan>
		</text>
		<text class="callout-label" x={margin + triW} y={margin + triH - 12} text-anchor="start">
			<tspan x={margin + triW + 10} dy="0">{CALLOUT_EVERYBODY}</tspan>
			<tspan x={margin + triW + 10} dy="1.05em">{CALLOUT_TRANSIT}</tspan>
		</text>
		<text class="callout-label" x={margin + triW/2} y={margin - 30} text-anchor="middle">
			<tspan x={margin + triW/2} dy="0">{CALLOUT_EVERYBODY}</tspan>
			<tspan x={margin + triW/2} dy="1.05em">{CALLOUT_ACTIVE}</tspan>
		</text>

		<!-- Data points -->
		{#each rows as row}
			<g>
				{#if (row.symbol && row.symbol.toLowerCase().includes('circle'))}
					<circle
						class="data-point"
						cx={row.x}
						cy={row.y}
						r={hoveredRow === row ? row.hoverPointSize : row.pointSize}
						fill={row.fill}
						stroke={row.stroke}
						stroke-width={hoveredRow === row ? 2 : 1.5}
						on:mouseenter={(e) => handlePointer(e, row)}
						on:mousemove={(e) => handlePointer(e, row)}
						on:mouseleave={hideTooltip}
					/>
				{:else if (row.symbol && row.symbol.toLowerCase().includes('square'))}
					<rect
						class="data-point"
						x={row.x - (hoveredRow === row ? row.hoverPointSize / 2 : row.pointSize / 2)}
						y={row.y - (hoveredRow === row ? row.hoverPointSize / 2 : row.pointSize / 2)}
						width={hoveredRow === row ? row.hoverPointSize : row.pointSize}
						height={hoveredRow === row ? row.hoverPointSize : row.pointSize}
						fill={row.fill}
						stroke={row.stroke}
						stroke-width={hoveredRow === row ? 2 : 1.5}
						on:mouseenter={(e) => handlePointer(e, row)}
						on:mousemove={(e) => handlePointer(e, row)}
						on:mouseleave={hideTooltip}
					/>
				{:else}
					<circle
						class="data-point"
						cx={row.x}
						cy={row.y}
						r={hoveredRow === row ? row.hoverPointSize : row.pointSize}
						fill={row.fill}
						stroke={row.stroke}
						stroke-width={hoveredRow === row ? 2 : 1.5}
						on:mouseenter={(e) => handlePointer(e, row)}
						on:mousemove={(e) => handlePointer(e, row)}
						on:mouseleave={hideTooltip}
					/>
				{/if}
				{#if row.label && (row.label.toLowerCase() === 'yes' || row.label.toLowerCase() === 'right')}
					<text x={row.x + 9} y={row.y + 4} class="point-label" text-anchor="start" alignment-baseline="middle">{row.short}</text>
				{:else if row.label && row.label.toLowerCase() === 'left'}
					<text x={row.x - 9} y={row.y + 4} class="point-label" text-anchor="end" alignment-baseline="middle">{row.short}</text>
				{/if}
			</g>
		{/each}
	</svg>

	{#if tooltip.show}
		<div class="tooltip" style="left: {tooltip.x}px; top: {tooltip.y}px;">
			<div class="tooltip-title">{tooltip.row.short}</div>
			<div>Motor vehicle: {tooltip.row.drive.toFixed(1)}%</div>
			<div>Public transit: {tooltip.row.transit.toFixed(1)}%</div>
			<div>Active (walk+bike): {tooltip.row.active.toFixed(1)}%</div>
		</div>
	{/if}

	<span style="font-size: 22px; padding-top: 20px;">↓</span>
</div>

</div>



<br><br>

<div class="text">



	<h1>About this chart</h1>
	<p>
		<a href="https://en.wikipedia.org/wiki/Ternary_plot" target="_blank">Ternary charts</a> are a type of visualization that show the composition of three-part data, where the three parts sum to a whole (e.g. 100% of trips). In transportation research, ternary charts can be used to show mode share: the percentage of trips made by different modes like driving, transit, and active transportation (walking/cycling). Each point on the chart represents a specific geographic area or population group, and its position within the triangle indicates the relative proportion of each travel mode. 
	</p>
	<p>
		The corners of the triangle represent 100% of one mode (e.g. all driving, all transit, or all active), while points along the edges represent combinations of two modes, and points within the interior represent combinations of all three modes (i.e. no single mode dominates). For example, looking by municipality, pre-amalgamated Toronto (Old Toronto) is quite close to the centre of the chart, indicating a more balanced mode share between driving, transit, and active travel. In contrast, in suburban and rural municipalities, more than 90% of trips are by motor vehicle, and thus they cluster near the bottom-left corner.
	</p>
	<p>
		In terms of demographics, the charts reveal that newcomers, teenagers, and young adults (especially women aged 15-24), as well as low-income households in Toronto are more likely to rely on public transit, with this mode comprising 30–43% of trips.
	</p>
	<p>	
		Torontonians residing close to the Ontario Line, TTC Line 1, or Line 2 predominantly walk or bike, with some Line 2 stations and most downtown stations showing a higher prevalence of public transit and active transportation over motor vehicles.
	</p>
	<p>
		While the chart is descriptive rather than causal, it can be used for exploratory analysis and supporting additional research. For example, planners could use these data to contextualize demographic differences in mobility as well as support corridor and station investments; researchers could use these charts as framing for deeper travel behaviour analyses or pilot projects.
	</p>
	<p>
		The data for this chart comes from the  <a href="https://dmg.utoronto.ca/tts-introduction/" target="_blank">Transportation Tomorrow Survey</a> (TTS), which is a large-scale household travel survey conducted in the Greater Golden Horseshoe (south-central Ontario) every 5 years. The TTS collects detailed information on travel behaviour, including mode share, trip purpose, and demographics, making it a useful resource for transportation planning and research in the region. The latest version of the survey (which is shown on the chart here) was conducted in 2022-23, so the patterns may have shifted since, but probably not substantially.
	</p>
	<p>
		If you are interested in maps showing mode share in the Toronto region, check out our <a href="./" target="_blank">interactive map</a> of Transportation Tomorrow Survey data, which includes mode share maps and other visualizations. We've also created a more experimental visualization of mode share across the  City of Toronto <a href="./mode-weave" target="_blank">using a "weaving-space" method</a>. Code for what is presented on this page is on <a href="https://github.com/schoolofcities/transportation-tomorrow-survey" target="_blank">GitHub</a>.
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





<style>
	.chart-wrap {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		/* padding: 12px; */
		position: relative;
		min-height: 300px;
		max-height: 1000px;
		height: 100vh;
		padding-top: 5px;
	}

	.chart-heading {
		font-family: TradeGothicBold, sans-serif;
		font-size: 37px;
		color: black;
		margin: 0px;
		line-height:45px;
		padding: 0px;
		padding-bottom: 15px;
		border: none;
	}

	.chart-subheading {
		font-family: Roboto, sans-serif;
		font-size: 16px;
		color: var(--brandBlack);
		margin: 0px;
		line-height: 22px;
		padding: 0px;
		padding-bottom: 32px;
		border: none;
	}

	svg {
		font-family: Roboto, sans-serif;
		border: solid 1px var(--brandGray);
		border-top: solid 8px black;
		border-bottom: solid 2px black;
	}

	@media (max-width: 870px) {
		svg {
			border-top-width: 4px;
			border-bottom-width: 1px;
		}
	}

	.svg-subtext {
		font-family: Roboto, sans-serif;
		font-size: 13px;
		color: #000000;
		margin-left: 15px;
	}

	.custom-dropdown {
		position: relative;
		width: calc(100% - 15px);
		margin-left: 15px;
		margin-bottom: 6px;
	}

	.dropdown-trigger {
		display: flex;
		align-items: center;
		width: 100%;
		box-sizing: border-box;
		padding: 6px 10px;
		border-radius: 4px;
		border: 1px solid #ccc;
		background: #fff;
		cursor: pointer;
		font-family: TradeGothicBold, sans-serif;
		font-size: 15px;
		transition: background-color 0.2s ease;
	}

	.dropdown-trigger:hover {
		background-color: #f5f5f5;
	}

	.dropdown-chevron {
		flex: 0 0 auto;
		font-size: 20px;
		line-height: 1;
		color: #333;
		margin-right: 4px;
	}

	.dropdown-label {
		flex: 1;
		text-align: right;
	}

	.dropdown-list {
		position: absolute;
		top: calc(100% + 2px);
		left: 0;
		right: 0;
		background: #fff;
		border: 1px solid #ccc;
		border-radius: 4px;
		padding: 2px 0;
		z-index: 9999;
		box-shadow: 0 4px 12px rgba(0,0,0,0.12);
	}

	.dropdown-list button {
		display: block;
		width: 100%;
		padding: 5px 10px;
		background: none;
		border: none;
		cursor: pointer;
		font-family: Roboto, sans-serif;
		font-size: 13px;
		text-align: right;
		color: #333;
	}

	.dropdown-list button:hover {
		background: #f5f5f5;
	}

	.dropdown-list button.active {
		font-weight: 600;
		color: #000;
	}

	.fo-right { position: relative; }
	.fo-author, .fo-date, .fo-data-source .fo-instructions  {
		font-family: Roboto, sans-serif;
		font-size: 12px;
		color: #555;
		margin-top: 6px;
	}

	.fo-data-source {
		position: absolute;
		right: 0;
		width: 160px;
		text-align: right;
		font-size: 12px;
		margin-top: 20px;
		color: #555;
		line-height: 1.4;
	}

	.fo-instructions {
		position: absolute;
		font-family: Roboto, sans-serif;
		right: 0;
		width: 160px;
		text-align: right;
		font-size: 12px;
		margin-top: 70px;
		color: #000000;
		line-height: 1.4;
	}

	.fo-left h1 { margin: 0; }

	.point-label {
		font-size: 13px;
		fill: #000000;
		pointer-events: none;
		opacity: 0.6
	}

	.vertex-label {
		font-size: 15px;
		fill: var(--brandGray80, #4d4d4d);
		text-transform: uppercase;
		letter-spacing: 0.02em;
	}

	.grid-line {
		stroke: #e0e0e0;
		stroke-width: 0.75;
		opacity: 0.95;
	}

	.grid-major {
		stroke: #c5c5c5;
		stroke-width: 1.5;
		opacity: 0.98;
	}

	.tick-label {
		font-size: 13px;
		fill: var(--brandGray80, #4d4d4d);
		font-weight: 500;
		pointer-events: none;
	}

	.tick-line {
		stroke: #2c2c2c;
		stroke-width: 2;
		pointer-events: none;
	}

	.hover-grid-line {
		stroke: #111;
		stroke-width: 1.6;
		stroke-dasharray: 6 4;
		opacity: 0.95;
		pointer-events: none;
	}

	.data-point { cursor: pointer; }

	.axis-title {
		font-size: 14px;
		fill: var(--brandGray80, #4d4d4d);
		text-transform: uppercase;
		letter-spacing: 0.02em;
		pointer-events: none;
	}

	.callout-label { 
		font-size: 16px;
		font-family: TradeGothicBold, sans-serif;
		fill: var(--brandBlack); 
		pointer-events: none; 
	}

	.area-polygon { pointer-events: none; }

	.tooltip {
		position: absolute;
		background: rgba(255,255,255,0.96);
		border: 1px solid #ddd;
		padding: 8px 10px;
		border-radius: 4px;
		box-shadow: 0 4px 10px rgba(0,0,0,0.08);
		pointer-events: none;
		font-size: 13px;
		color: #111;
		min-width: 140px;
	}

	.tooltip-title {
		font-family: TradeGothicBold;
		margin-bottom: 4px;
		font-size: 16px;
	}

	@media (max-width: 500px) {
		.tooltip {
			font-size: 9px;
			padding: 5px 7px;
			min-width: 90px;
		}
		.tooltip-title {
			font-size: 11px;
		}
	}

	@media (max-width: 870px) and (min-width: 501px) {
		.tooltip {
			font-size: 11px;
			padding: 6px 8px;
			min-width: 115px;
		}
		.tooltip-title {
			font-size: 13px;
		}
	}

	a {
		color: var(--brandBlack);
		text-decoration: underline
	}

	a:hover {
		color: var(--brandDarkBlue);
	}

</style>
