# Run with streamlit run dashboards/app.py

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import base64
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

from src.viz.dashboard_queries import (
    get_station_list,
    get_climate_timeseries,
    get_bloom_forecast,
    get_bloom_history,
    get_bloom_temp_features,
    get_sakura_forecast_map,
)

from src.viz.plots import (
    plot_sakura_forecast_map,
    plot_sakura_bloom_timeline,
)

from src.viz.cards import render_forecast_section

def add_floating_petals(image_path: str):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .petal-overlay {{
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: 9999;
            overflow: hidden;
        }}

        .petal {{
            position: absolute;
            width: 25px;
            opacity: 1;
            animation-name: fallDrift;
            animation-timing-function: linear;
            animation-iteration-count: infinite;
        }}

        .petal img {{
            width: 100%;
            display: block;
        }}

        .petal-1 {{ left: 15%; top: -10%; animation-duration: 28s; animation-delay: 0s; }}
        .petal-2 {{ left: 55%; top: -15%; animation-duration: 30s; animation-delay: 5s; }}
        .petal-3 {{ left: 80%; top: -12%; animation-duration: 32s; animation-delay: 10s; }}

        @keyframes fallDrift {{
            0% {{ transform: translateY(-10vh) translateX(0px) rotate(0deg); }}
            25% {{ transform: translateY(25vh) translateX(20px) rotate(35deg); }}
            50% {{ transform: translateY(50vh) translateX(-15px) rotate(85deg); }}
            75% {{ transform: translateY(75vh) translateX(18px) rotate(140deg); }}
            100% {{ transform: translateY(110vh) translateX(-10px) rotate(200deg); }}
        }}
        </style>

        <div class="petal-overlay">
            <div class="petal petal-1"><img src="data:image/png;base64,{encoded}" /></div>
            <div class="petal petal-2"><img src="data:image/png;base64,{encoded}" /></div>
            <div class="petal petal-3"><img src="data:image/png;base64,{encoded}" /></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.set_page_config(
    page_title="Seasonal Japan", 
    page_icon="🌸", 
    layout="wide"
)

add_floating_petals("dashboards/assets/sakura_petal.png")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;0,6..72,500;1,6..72,300;1,6..72,400&family=Schibsted+Grotesk:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@300;400;500;600&family=Shippori+Mincho:wght@400;500;600;700&display=swap');

:root {
    --bg:          #15131b;
    --bg-card:     #1d1622;
    --bg-card-alt: #181420;
    --border:      rgba(255,255,255,.08);
    --pink:        #ff8fa9;
    --pink-muted:  #e69bb4;
    --text:        #f6f1f4;
    --text-muted:  #b1aabf;
    --text-dim:    #948fa0;
    --text-faint:  #6f6a80;
    --mono:        'IBM Plex Mono', monospace;
    --serif:       'Newsreader', serif;
    --jp:          'Shippori Mincho', serif;
    --sans:        'Schibsted Grotesk', sans-serif;
}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
section.main {
    background-color: var(--bg) !important;
    font-family: var(--sans) !important;
    color: var(--text) !important;
}

[data-testid="stHeader"] { background: transparent; }

.block-container {
    max-width: 100% !important;
    padding-left: 3rem !important;
    padding-right: 3rem !important;
}

[data-testid="stPlotlyChart"] {
    background: transparent !important;
    border-radius: 0 !important;
    padding: 0 !important;
    box-shadow: none !important;
    overflow: visible !important;
}

[data-testid="stPlotlyChart"] > div,
[data-testid="stPlotlyChart"] .js-plotly-plot,
[data-testid="stPlotlyChart"] .plot-container,
[data-testid="stPlotlyChart"] .svg-container {
    background: transparent !important;
}

div[data-testid="column"] {
    display: flex;
    align-self: stretch;
}

div[data-testid="column"] > div { width: 100%; }

/* ── Cards ────────────────────────────────────────────── */
.st-key-timeline_card,
.st-key-visit_card,
.st-key-highlights_card,
.st-key-spots_card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 22px 24px;
    min-height: 380px;
    box-sizing: border-box;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
}

.st-key-timeline_card h3,
.st-key-visit_card h3,
.st-key-highlights_card h3,
.st-key-spots_card h3 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text);
    margin-top: 0 !important;
    padding-top: 0 !important;
    margin-bottom: 0.7rem;
    line-height: 1.2;
}

.muted-text {
    color: var(--text-dim);
    font-size: 0.9rem;
    line-height: 1.5;
}

/* ── Best-time-to-visit card ────────────────────────── */
.best-visit-card {
    height: 100%;
    display: flex;
    flex-direction: column;
    color: var(--text);
    justify-content: space-between;
}

.best-visit-card h3 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text);
    margin: 0 !important;
    padding: 0 !important;
    margin-bottom: 0.7rem !important;
    line-height: 1.2;
}

.best-visit-subtitle {
    color: var(--text-dim);
    font-size: 0.9rem;
    line-height: 1.45;
    margin: 0 0 1rem 0;
}

.visit-timeline-labels {
    position: relative;
    height: 40px;
    margin-top: 0.1rem;
}

.timeline-label {
    position: absolute;
    top: 2px;
    transform: translateX(-50%);
    text-align: center;
}

.timeline-label span {
    font-size: 0.70rem;
    line-height: 1;
    font-weight: 400;
    white-space: nowrap;
    display: block;
    text-align: center;
    color: var(--text-muted);
}

.label-first  { left: 25%; }
.label-peak   { left: 50%; }
.label-best   { left: 75%; }

.label-first span  { color: #8FC89A; }
.label-peak span   { color: var(--pink); }
.label-best span   { color: var(--text-muted); }

.dotted-line {
    width: 1px;
    height: 18px;
    margin: 4px auto 0 auto;
    background-size: 1px 7px;
    background-repeat: repeat-y;
    opacity: 0.6;
}

.label-first .dotted-line { background-image: linear-gradient(to bottom, #8FC89A 45%, transparent 0%); }
.label-peak  .dotted-line { background-image: linear-gradient(to bottom, var(--pink) 45%, transparent 0%); }
.label-best  .dotted-line { background-image: linear-gradient(to bottom, var(--text-muted) 45%, transparent 0%); }

.visit-timeline-wrap {
    position: relative;
    height: 42px;
    margin-top: 0.1rem;
}

.timeline-pale-track {
    position: absolute;
    left: 0; right: 0; top: 13px;
    height: 22px;
    border-radius: 999px;
    background: rgba(255,255,255,.07);
}

.timeline-visit-window {
    position: absolute;
    left: 25%; right: 10%; top: 13px;
    height: 22px;
    border-radius: 999px;
    background: rgba(255,143,169,.18);
}

.timeline-peak-window {
    position: absolute;
    left: 35%; right: 38%; top: 17px;
    height: 14px;
    border-radius: 999px;
    background: var(--pink);
    box-shadow: 0 0 12px rgba(255,143,169,.6);
}

.timeline-dot {
    position: absolute;
    top: 10px;
    width: 7px; height: 7px;
    border-radius: 999px;
    transform: translateX(-50%);
    z-index: 5;
}

.dot-first { left: 25%; background: #8FC89A; }
.dot-peak  { left: 50%; background: var(--pink); box-shadow: 0 0 8px var(--pink); }
.dot-best  { left: 75%; background: var(--text-muted); }

.timeline-axis {
    position: relative;
    height: 52px;
    margin: 0.45rem 0 0.8rem 0;
}

.axis-line {
    position: absolute;
    top: 10px; left: 0; right: 0;
    height: 1px;
    background: rgba(255,255,255,.12);
}

.axis-tick {
    position: absolute;
    top: 0;
    transform: translateX(-50%);
    text-align: center;
}

.tick-one   { left: 12%; }
.tick-two   { left: 38%; }
.tick-three { left: 64%; }
.tick-four  { left: 92%; }

.tick-mark {
    width: 1px; height: 17px;
    margin: 0 auto 7px auto;
    background: rgba(255,255,255,.2);
}

.tick-date {
    font-size: 0.72rem;
    line-height: 1.18;
    font-weight: 500;
    color: var(--text-dim);
    font-family: var(--mono);
}

.visit-detail-section { margin-top: auto; }

.visit-detail-row {
    display: grid;
    grid-template-columns: 10px minmax(0,1fr);
    gap: 0.65rem;
    align-items: start;
    padding: 0.25rem 0;
}

.visit-detail-dot {
    width: 8px; height: 8px;
    margin-top: 0.45rem;
    border-radius: 999px;
    background: #8FC89A;
}

.visit-detail-dot.medium { background: var(--text-muted); }
.visit-detail-dot.bright { background: var(--pink); box-shadow: 0 0 8px var(--pink); }

.visit-detail-label {
    font-size: 0.75rem;
    color: var(--text-dim);
    font-weight: 500;
    margin-bottom: 0.2rem;
    font-family: var(--mono);
    letter-spacing: 0.5px;
}

.visit-detail-value {
    font-size: 1rem;
    line-height: 1.25;
    color: var(--text);
    font-weight: 300;
    font-family: var(--serif);
    white-space: nowrap;
}

.visit-row-line {
    height: 1px;
    background: var(--border);
    margin: 0.4rem 0;
}

</style>
""",
    unsafe_allow_html=True,
)

# Stations

stations = get_station_list()

station_label_map = {
    row["station_name"]: row["station_code"]
    for _, row in stations.iterrows()
}

options = list(station_label_map.keys())
default_index = options.index("TOKYO") if "TOKYO" in options else 0

reverse_station_label_map = {
    str(v): k for k, v in station_label_map.items()
}

if "selected_station_name" not in st.session_state:
    st.session_state["selected_station_name"] = options[default_index]

if "station_selector" not in st.session_state:
    st.session_state["station_selector"] = st.session_state["selected_station_name"]

selected_name = st.session_state["selected_station_name"]
selected_station_code = station_label_map[selected_name]

# Hero + Map

map_df = get_sakura_forecast_map(year=2026)
clicked_station_code = None

# Apply any pending map-click station before the selectbox widget is instantiated
if "pending_station_name" in st.session_state:
    st.session_state["station_selector"] = st.session_state.pop("pending_station_name")

# ── Topbar ────────────────────────────────────────────────────────────────────
topbar_left, topbar_right = st.columns([0.75, 1.25], gap="large")

with topbar_left:
    st.markdown(
        "<div style=\""
        "font: 500 12px/1 'IBM Plex Mono', monospace;"
        "letter-spacing: 2px;"
        "color: #e69bb4;"
        "padding-top: 2rem;"
        "\">桜前線 &mdash; Sakura forecast</div>",
        unsafe_allow_html=True,
    )

with topbar_right:
    selected_name = st.selectbox(
        label="City",
        options=options,
        key="station_selector",
        label_visibility="collapsed",
    )
    if selected_name != st.session_state["selected_station_name"]:
        st.session_state["selected_station_name"] = selected_name
        if "sakura_map" in st.session_state:
            del st.session_state["sakura_map"]
        st.rerun()

selected_station_code = station_label_map[st.session_state["selected_station_name"]]

hero_left, hero_right = st.columns([0.75, 1.25], gap="large")

with hero_left:
    st.markdown(
        """
        <div style="padding-top:3.5rem;padding-left:0.5rem;">
            <h2 style="
                font: 300 58px/1.04 'Newsreader', serif;
                color: #f6f1f4;
                margin: 0 0 24px;
                letter-spacing: -0.5px;
            ">When will the&nbsp;<em style="font-style:italic;font-weight:400;color:#ff8fa9;">sakura</em><br>bloom?</h2>
            <p style="
                font: 300 18px/1.6 'Newsreader', serif;
                color: #b1aabf;
                max-width: 430px;
                margin: 0;
            ">Choose a city, and we'll pinpoint the days when its blossoms are at their most radiant. Plan your trip around this fleeting season, and experience the rare week each year when the trees transform the streets into a world of petals and light.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with hero_right:
    if map_df.empty:
        st.info("No forecast map data available.")
    else:
        fig_map = plot_sakura_forecast_map(
            map_df,
            selected_station_code=selected_station_code,
        )

        map_event = st.plotly_chart(
            fig_map,
            width="stretch",
            key="sakura_map",
            on_select="rerun",
            selection_mode="points",
            config={
                "displayModeBar": False,
                "scrollZoom": False,
                "doubleClick": False,
                "staticPlot": False,
            },
        )

        components.html("""
<script>
(function() {
    var doc = window.parent.document;
    var win = window.parent;
    var svgNS = 'http://www.w3.org/2000/svg';
    var STROKE = 'rgba(255,143,169,0.6)';
    var DIAG = 44;

    function getOrCreateOverlay(plotDiv) {
        var existing = plotDiv.querySelector('#sakura-callout-overlay');
        if (existing) return existing;
        var svg = doc.createElementNS(svgNS, 'svg');
        svg.id = 'sakura-callout-overlay';
        svg.style.cssText =
            'position:absolute;top:0;left:0;width:100%;height:100%;' +
            'pointer-events:none;overflow:visible;z-index:10;';
        if (getComputedStyle(plotDiv).position === 'static') {
            plotDiv.style.position = 'relative';
        }
        plotDiv.appendChild(svg);
        return svg;
    }

    function clearOverlay(svg) {
        while (svg.lastChild) svg.removeChild(svg.lastChild);
    }

    function getDotPos(plotDiv, lon, lat, mouseEvent) {
        var pRect = plotDiv.getBoundingClientRect();
        try {
            var subplot = plotDiv._fullLayout.geo._subplot;
            if (subplot && subplot.projection) {
                var pos = subplot.projection([lon, lat]);
                if (pos && !isNaN(pos[0]) && !isNaN(pos[1])) {
                    var svgEl = plotDiv.querySelector('svg.main-svg');
                    var ox = svgEl ? svgEl.getBoundingClientRect().left - pRect.left : 0;
                    var oy = svgEl ? svgEl.getBoundingClientRect().top  - pRect.top  : 0;
                    return { x: pos[0] + ox, y: pos[1] + oy };
                }
            }
        } catch(e) {}
        return { x: mouseEvent.clientX - pRect.left, y: mouseEvent.clientY - pRect.top };
    }

    function drawCallout(svg, plotDiv, lon, lat, mouseEvent, cityName, dateStr, marginStr) {
        clearOverlay(svg);

        var dot = getDotPos(plotDiv, lon, lat, mouseEvent);
        var px = dot.x, py = dot.y;
        var plotRect = plotDiv.getBoundingClientRect();
        var goRight = px < plotRect.width / 2;
        var dir = goRight ? 1 : -1;

        var ex = px + dir * DIAG;
        var ey = py - DIAG;

        var ring = doc.createElementNS(svgNS, 'circle');
        ring.setAttribute('cx', px);
        ring.setAttribute('cy', py);
        ring.setAttribute('r', '9');
        ring.setAttribute('fill', 'none');
        ring.setAttribute('stroke', 'rgba(255,255,255,0.85)');
        ring.setAttribute('stroke-width', '2');
        svg.appendChild(ring);

        function mkTxt(content, family, size, weight) {
            var t = doc.createElementNS(svgNS, 'text');
            t.setAttribute('font-family', family);
            t.setAttribute('font-size', size);
            t.setAttribute('font-weight', weight);
            t.setAttribute('visibility', 'hidden');
            t.textContent = content;
            svg.appendChild(t);
            return t;
        }

        var tName   = mkTxt(cityName,   "'Newsreader', serif",        '14', '400');
        var tDate   = mkTxt(dateStr,    "'IBM Plex Mono', monospace",  '12', '500');
        var tMargin = marginStr ? mkTxt(marginStr, "'IBM Plex Mono', monospace", '10', '400') : null;

        var barW = Math.max(tName.getComputedTextLength(), tDate.getComputedTextLength());
        if (tMargin && tMargin.getComputedTextLength() > barW) barW = tMargin.getComputedTextLength();

        var anchor = goRight ? 'start' : 'end';
        var barX2  = ex + dir * barW;

        var diag = doc.createElementNS(svgNS, 'line');
        diag.setAttribute('x1', px); diag.setAttribute('y1', py);
        diag.setAttribute('x2', ex); diag.setAttribute('y2', ey);
        diag.setAttribute('stroke', STROKE);
        diag.setAttribute('stroke-width', '1');
        svg.appendChild(diag);

        var bar = doc.createElementNS(svgNS, 'line');
        bar.setAttribute('x1', ex);    bar.setAttribute('y1', ey);
        bar.setAttribute('x2', barX2); bar.setAttribute('y2', ey);
        bar.setAttribute('stroke', STROKE);
        bar.setAttribute('stroke-width', '1');
        svg.appendChild(bar);

        tName.setAttribute('x', ex);
        tName.setAttribute('y', ey - (tMargin ? 31 : 19));
        tName.setAttribute('text-anchor', anchor);
        tName.setAttribute('fill', '#f4eff4');
        tName.setAttribute('visibility', 'visible');

        tDate.setAttribute('x', ex);
        tDate.setAttribute('y', ey - (tMargin ? 17 : 5));
        tDate.setAttribute('text-anchor', anchor);
        tDate.setAttribute('fill', '#f4eff4');
        tDate.setAttribute('visibility', 'visible');

        if (tMargin) {
            tMargin.setAttribute('x', ex);
            tMargin.setAttribute('y', ey - 3);
            tMargin.setAttribute('text-anchor', anchor);
            tMargin.setAttribute('fill', 'rgba(244,239,244,0.5)');
            tMargin.setAttribute('visibility', 'visible');
        }
    }

    function isMapPlot(plotDiv) {
        return plotDiv._fullData &&
               plotDiv._fullData.some(function(t) { return t.type === 'scattergeo'; });
    }

    function attachToPlot(plotDiv) {
        if (plotDiv._sakuraCalloutAttached) return;
        if (!plotDiv._fullData) return;
        if (!isMapPlot(plotDiv)) { plotDiv._sakuraCalloutAttached = true; return; }

        plotDiv._sakuraCalloutAttached = true;
        var svg = getOrCreateOverlay(plotDiv);
        var activeStation = null;

        plotDiv.on('plotly_hover', function(data) {
            var pt = null;
            for (var i = 0; i < data.points.length; i++) {
                var p = data.points[i];
                if (p.customdata && Array.isArray(p.customdata) && p.customdata.length > 6) {
                    pt = p; break;
                }
            }
            if (!pt) return;
            var code = pt.customdata[0];
            if (code === activeStation) return;
            activeStation = code;
            drawCallout(svg, plotDiv, pt.lon, pt.lat, data.event, pt.text || '', pt.customdata[6] || '', pt.customdata[7] || '');
        });

        plotDiv.on('plotly_unhover', function() {
            activeStation = null;
            clearOverlay(svg);
        });
    }

    function findAndAttach() {
        doc.querySelectorAll('.js-plotly-plot').forEach(attachToPlot);
    }

    setTimeout(findAndAttach, 400);
    setTimeout(findAndAttach, 1000);
    setTimeout(findAndAttach, 2500);

    if (!win._sakuraCalloutObserver) {
        win._sakuraCalloutObserver = new MutationObserver(function() {
            setTimeout(findAndAttach, 300);
        });
        win._sakuraCalloutObserver.observe(doc.body, {childList: true, subtree: true});
    }
})();
</script>
""", height=0)

        if map_event and map_event.selection.points:
            clicked_point = map_event.selection.points[0]
            clicked_station_code = str(clicked_point["customdata"][0])

# Update selected station based on map click

if (
    clicked_station_code
    and clicked_station_code in reverse_station_label_map
    and clicked_station_code != str(station_label_map[st.session_state["selected_station_name"]])
):
    new_name = reverse_station_label_map[clicked_station_code]
    st.session_state["selected_station_name"] = new_name
    st.session_state["pending_station_name"] = new_name
    st.rerun()

selected_name = st.session_state["selected_station_name"]
selected_station_code = station_label_map[selected_name]
selected_location_code = str(int(selected_station_code) - 47000)
selected_n_years = 20

# Load data

bloom_history_df = get_bloom_history(selected_location_code)
bloom_temp_df = get_bloom_temp_features(selected_station_code, selected_location_code)
forecast_df = get_bloom_forecast(selected_location_code, year=2026)

df = get_climate_timeseries(selected_station_code)

if df.empty:
    st.warning("No climate data found for this station.")
    st.stop()

# Prepare data

df["date_key"] = pd.to_datetime(df["date_key"])
df["year"] = df["date_key"].dt.year

if not bloom_history_df.empty:
    bloom_history_df["date_key"] = pd.to_datetime(bloom_history_df["date_key"])
    bloom_history_df["year"] = bloom_history_df["year"].astype(int)

if not bloom_temp_df.empty:
    bloom_temp_df["date_key"] = pd.to_datetime(bloom_temp_df["date_key"])
    bloom_temp_df["year"] = bloom_temp_df["year"].astype(int)

reference_year = 2026

if not forecast_df.empty:
    reference_year = int(forecast_df.loc[0, "forecast_year"])

min_year_to_keep = reference_year - selected_n_years + 1

if not bloom_history_df.empty:
    bloom_history_df = bloom_history_df[bloom_history_df["year"] >= min_year_to_keep]

if not bloom_temp_df.empty:
    bloom_temp_df = bloom_temp_df[bloom_temp_df["year"] >= min_year_to_keep]

# Forecast info

if not forecast_df.empty and pd.notna(forecast_df.loc[0, "predicted_event_date"]):
    bloom_date = pd.to_datetime(forecast_df.loc[0, "predicted_event_date"]).strftime("%d %b %Y")
    model_name = forecast_df.loc[0, "model_name"]
    forecast_updated_at = pd.to_datetime(forecast_df.loc[0, "trained_at"]).strftime("%d %b %Y")
else:
    bloom_date = "Not available"
    model_name = "Not available"
    forecast_updated_at = "Not available"

model_label_map = {
    "linear_regression": "Linear Regression",
    "random_forest": "Random Forest",
    "hist_gradient_boosting": "Histogram Gradient Boosting",
}

# ── Forecast section ─────────────────────────────────────────────────────────
forecast_html = render_forecast_section(
    station_name=selected_name,
    forecast_df=forecast_df,
)
if forecast_html:
    st.html(forecast_html)

# ── Through the years ─────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="border-top:1px solid rgba(255,255,255,.1);padding-top:30px;margin-top:76px;">
        <div style="font:500 12px/1 'IBM Plex Mono',monospace;letter-spacing:2px;color:#e69bb4;margin-bottom:8px;">
            二十年の記録 &mdash; Through the years
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

years_left, years_right = st.columns([0.9, 1.1], gap="large")

with years_left:
    st.markdown(
        f"""
        <div style="padding-top:0.5rem;">
            <h3 style="font:300 28px/1.15 'Newsreader',serif;color:#f6f1f4;margin:0 0 14px;">
                The bloom keeps creeping <em style="font-style:italic;color:#ff8fa9;">earlier</em>.
            </h3>
            <p style="font:300 15px/1.6 'Newsreader',serif;color:#b1aabf;margin:0;">
                Two decades of {selected_name.title()} first-bloom dates from the Japan Meteorological Agency
                — one dot per spring. The trend drifts steadily earlier as the city warms.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with years_right:
    fig_timeline = plot_sakura_bloom_timeline(bloom_history_df, forecast_df)
    st.plotly_chart(
        fig_timeline,
        width="stretch",
        config={"displayModeBar": False},
    )

# ── Where & how to see it ────────────────────────────────────────────────────
st.html("""
<style>
@media (max-width: 640px) {
    .hanami-grid { grid-template-columns: 1fr !important; gap: 28px !important; }
}
</style>
<div style="border-top:1px solid rgba(255,255,255,.1);padding-top:30px;margin-top:76px;">
    <div style="font:500 12px/1 'IBM Plex Mono',monospace;letter-spacing:2px;color:#e69bb4;margin-bottom:22px;">
        花見 &mdash; Where &amp; how to see it
    </div>
    <div class="hanami-grid" style="display:grid;grid-template-columns:1fr 1.05fr 1fr;gap:36px;">

        <!-- famous spots -->
        <div>
            <div style="font:600 16px/1 'Shippori Mincho',serif;color:#f4eff4;margin-bottom:5px;">
                名所 <span style="font:500 14px 'Schibsted Grotesk',sans-serif;color:#948fa0;">Famous spots</span>
            </div>
            <p style="font:300 14px/1.5 'Newsreader',serif;font-style:italic;color:#948fa0;margin:0 0 14px;">
                Where Tokyo gathers to look up.
            </p>
            <div style="display:flex;justify-content:space-between;align-items:baseline;border-top:1px solid rgba(255,255,255,.08);padding:10px 0;">
                <span style="font:300 16px 'Newsreader',serif;color:#eee8f0;">Chidorigafuchi</span>
                <span style="font:500 11px 'IBM Plex Mono',monospace;color:#6f6a80;">Chiyoda</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:baseline;border-top:1px solid rgba(255,255,255,.08);padding:10px 0;">
                <span style="font:300 16px 'Newsreader',serif;color:#eee8f0;">Meguro River</span>
                <span style="font:500 11px 'IBM Plex Mono',monospace;color:#6f6a80;">Meguro</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:baseline;border-top:1px solid rgba(255,255,255,.08);padding:10px 0;">
                <span style="font:300 16px 'Newsreader',serif;color:#eee8f0;">Ueno Park</span>
                <span style="font:500 11px 'IBM Plex Mono',monospace;color:#6f6a80;">Tait&#333;</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:baseline;border-top:1px solid rgba(255,255,255,.08);padding:10px 0;">
                <span style="font:300 16px 'Newsreader',serif;color:#eee8f0;">Shinjuku Gyoen</span>
                <span style="font:500 11px 'IBM Plex Mono',monospace;color:#6f6a80;">Shinjuku</span>
            </div>
        </div>

        <!-- how to hanami -->
        <div>
            <div style="font:600 16px/1 'Shippori Mincho',serif;color:#f4eff4;margin-bottom:5px;">
                花見の楽しみ方 <span style="font:500 14px 'Schibsted Grotesk',sans-serif;color:#948fa0;">How to hanami</span>
            </div>
            <p style="font:300 15px/1.6 'Newsreader',serif;color:#cfc6d6;margin:0 0 14px;">
                Lay a mat under the trees, share food slowly, and let the afternoon drift.
                As dusk falls the lanterns come on and the blossoms turn a deeper pink —
                <em style="font-style:italic;">yozakura</em>, evening hanami, when the crowds thin and the petals glow.
            </p>
            <div style="display:flex;gap:10px;">
                <div style="flex:1;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);
                    border-radius:11px;padding:12px 14px;">
                    <div style="font:500 10px/1 'IBM Plex Mono',monospace;letter-spacing:1px;
                        color:#e69bb4;text-transform:uppercase;margin-bottom:6px;">昼 Day</div>
                    <div style="font:300 14px/1.4 'Newsreader',serif;color:#eee8f0;">Picnics &amp; mats from late morning.</div>
                </div>
                <div style="flex:1;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);
                    border-radius:11px;padding:12px 14px;">
                    <div style="font:500 10px/1 'IBM Plex Mono',monospace;letter-spacing:1px;
                        color:#e69bb4;text-transform:uppercase;margin-bottom:6px;">夜 Night</div>
                    <div style="font:300 14px/1.4 'Newsreader',serif;color:#eee8f0;">Lit blossoms, quieter paths.</div>
                </div>
            </div>
        </div>

        <!-- taste of spring -->
        <div>
            <div style="font:600 16px/1 'Shippori Mincho',serif;color:#f4eff4;margin-bottom:5px;">
                春の味 <span style="font:500 14px 'Schibsted Grotesk',sans-serif;color:#948fa0;">Taste of spring</span>
            </div>
            <p style="font:300 15px/1.55 'Newsreader',serif;font-style:italic;color:#948fa0;margin:0 0 14px;">
                Seasonal sweets to carry to the picnic.
            </p>
            <div style="display:flex;align-items:center;gap:12px;background:rgba(255,255,255,.05);
                border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:11px 14px;margin-bottom:9px;">
                <span style="width:22px;height:22px;border-radius:50%;background:#EFB6C4;flex-shrink:0;
                    box-shadow:0 0 12px rgba(239,182,196,.5);"></span>
                <div style="font:300 16px/1 'Newsreader',serif;color:#eee8f0;">桜餅 Sakura mochi</div>
            </div>
            <div style="display:flex;align-items:center;gap:12px;background:rgba(255,255,255,.05);
                border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:11px 14px;margin-bottom:9px;">
                <span style="width:22px;height:22px;border-radius:50%;
                    background:linear-gradient(180deg,#EFB6C4 33%,#efe8ee 33% 66%,#B9CFA6 66%);
                    flex-shrink:0;box-shadow:0 0 12px rgba(239,182,196,.4);"></span>
                <div style="font:300 16px/1 'Newsreader',serif;color:#eee8f0;">花見団子 Hanami dango</div>
            </div>
            <div style="display:flex;align-items:center;gap:12px;background:rgba(255,255,255,.05);
                border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:11px 14px;">
                <span style="width:22px;height:22px;border-radius:50%;background:#E6CBB0;flex-shrink:0;
                    box-shadow:0 0 12px rgba(230,203,176,.4);"></span>
                <div style="font:300 16px/1 'Newsreader',serif;color:#eee8f0;">桜ラテ Sakura latte</div>
            </div>
        </div>
    </div>
</div>
""")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="margin-top:64px;padding-top:15px;border-top:1px solid rgba(255,255,255,.1);
        font:300 italic 13px/1.4 'Newsreader',serif;color:#6f6a80;">
        出典 Source &mdash; Japan Meteorological Agency &nbsp;·&nbsp;
        {model_label_map.get(model_name, model_name)} &nbsp;·&nbsp;
        Updated {forecast_updated_at}
    </div>
    """,
    unsafe_allow_html=True,
)