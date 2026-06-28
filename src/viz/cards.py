import math
import textwrap

import pandas as pd


def format_card_date(date) -> str:
    if date is None or pd.isna(date):
        return "N/A"

    date = pd.to_datetime(date)
    return date.strftime("%d<br>%b")


def format_inline_date(date) -> str:
    if date is None or pd.isna(date):
        return "N/A"

    return pd.to_datetime(date).strftime("%d %b %Y")


def format_range_compact(start_date, end_date) -> str:
    if start_date is None or end_date is None:
        return "Not available"

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    return f"{start_date.strftime('%d %b')} – {end_date.strftime('%d %b %Y')}"


_DEFAULT_FULL_BLOOM_GAP = 8  # fallback when no historical gap data exists for a station


def get_best_visit_dates(forecast_df: pd.DataFrame, full_bloom_gap_days: int | None = None) -> dict:
    if forecast_df.empty or pd.isna(forecast_df.iloc[0]["predicted_event_date"]):
        return {"available": False}

    first_bloom = pd.to_datetime(forecast_df.iloc[0]["predicted_event_date"])
    gap = full_bloom_gap_days if full_bloom_gap_days is not None else _DEFAULT_FULL_BLOOM_GAP

    full_bloom = first_bloom + pd.Timedelta(days=gap)
    peak_start = full_bloom - pd.Timedelta(days=1)
    peak_end = full_bloom + pd.Timedelta(days=1)

    visit_start = peak_start - pd.Timedelta(days=2)
    visit_end = peak_end + pd.Timedelta(days=4)

    hanafubuki_start = full_bloom + pd.Timedelta(days=3)
    hanafubuki_end = full_bloom + pd.Timedelta(days=10)

    return {
        "available": True,
        "first_bloom": first_bloom,
        "full_bloom": full_bloom,
        "peak_start": peak_start,
        "peak_end": peak_end,
        "visit_start": visit_start,
        "visit_end": visit_end,
        "hanafubuki_start": hanafubuki_start,
        "hanafubuki_end": hanafubuki_end,
    }


def _interp_bloom_color(t: float) -> str:
    """Pale pink at first bloom → #f2959d at peak → background at petal fall."""
    stops = [
        (0.00, (249, 221, 223)),  # very pale pink
        (0.50, (242, 149, 157)),  # #f2959d — full bloom
        (1.00, ( 21,  19,  27)),  # #15131b — background
    ]
    for i in range(len(stops) - 1):
        t0, c0 = stops[i]
        t1, c1 = stops[i + 1]
        if t <= t1:
            u = (t - t0) / (t1 - t0)
            r = round(c0[0] + (c1[0] - c0[0]) * u)
            g = round(c0[1] + (c1[1] - c0[1]) * u)
            b = round(c0[2] + (c1[2] - c0[2]) * u)
            return f"rgb({r},{g},{b})"
    lc = stops[-1][1]
    return f"rgb({lc[0]},{lc[1]},{lc[2]})"


def _early_late_badge(forecast_doy: int, hist_avg_doy: int | None) -> str:
    if hist_avg_doy is None:
        return ""
    delta = forecast_doy - hist_avg_doy
    if abs(delta) <= 1:
        label = "On track — within a day of the 20-year average"
        color = "#948fa0"
    elif delta < 0:
        label = f"{abs(delta)} day{'s' if abs(delta) != 1 else ''} earlier than the 20-year average"
        color = "#ff8fa9"
    else:
        label = f"{delta} day{'s' if delta != 1 else ''} later than the 20-year average"
        color = "#7eb8c9"
    return (
        f'<span style="font:500 11px/1 \'IBM Plex Mono\',monospace;letter-spacing:0.5px;'
        f'color:{color};border:1px solid {color};border-radius:20px;'
        f'padding:3px 10px;white-space:nowrap;">{label}</span>'
    )


def _accuracy_note(station_mae: float | None, global_mae: float | None) -> str:
    mae = station_mae if station_mae is not None else global_mae
    if mae is None:
        return ""
    if mae > 20:
        return (
            '<p style="font:300 italic 13px/1.4 \'Newsreader\',serif;color:#b08a6a;margin:12px 0 0;">'
            "Forecast reliability is lower for this region — allow extra flexibility when planning."
            "</p>"
        )
    return (
        f'<p style="font:300 italic 13px/1.4 \'Newsreader\',serif;color:#948fa0;margin:12px 0 0;">'
        f"Forecast accuracy: typically within ±{mae:.0f} days for this station."
        f"</p>"
    )


def _estimated_tag(prediction_status: str | None) -> str:
    if prediction_status != "estimated":
        return ""
    return (
        '<span style="font:500 10px/1 \'IBM Plex Mono\',monospace;letter-spacing:1px;'
        'color:#e69bb4;border:1px solid rgba(230,155,180,0.4);border-radius:20px;'
        'padding:2px 8px;margin-left:8px;vertical-align:middle;">'
        "USES CLIMATE NORMALS"
        "</span>"
    )


def render_forecast_section(
    station_name: str,
    forecast_df: pd.DataFrame,
    hist_avg_doy: int | None = None,
    full_bloom_gap_days: int | None = None,
) -> str:
    dates = get_best_visit_dates(forecast_df, full_bloom_gap_days=full_bloom_gap_days)
    if not dates["available"]:
        return ""

    first_bloom      = dates["first_bloom"]
    full_bloom       = dates["full_bloom"]
    peak_start       = dates["peak_start"]
    peak_end         = dates["peak_end"]
    visit_start      = dates["visit_start"]
    visit_end        = dates["visit_end"]
    hanafubuki_start = dates["hanafubuki_start"]
    hanafubuki_end   = dates["hanafubuki_end"]

    row = forecast_df.iloc[0]
    station_mae = float(row["station_mae_days"]) if pd.notna(row.get("station_mae_days")) else None
    global_mae  = float(row["mae_days"]) if pd.notna(row.get("mae_days")) else None
    prediction_status = str(row.get("prediction_status", "")) or None

    n_days = (hanafubuki_end - first_bloom).days + 2
    cal_days = [first_bloom + pd.Timedelta(days=i) for i in range(n_days)]

    # peak centre is full bloom day
    peak_center_idx = (full_bloom - first_bloom).days

    best_s = max(0, (visit_start - first_bloom).days)
    best_e = min(n_days - 1, (visit_end - first_bloom).days)

    cell_pct = 100.0 / n_days
    bv_left  = f"{best_s * cell_pct:.1f}%"
    bv_width = f"{(best_e - best_s + 1) * cell_pct:.1f}%"

    cells_html = ""
    for i, day in enumerate(cal_days):
        if peak_center_idx > 0 and i <= peak_center_idx:
            ct = (i / peak_center_idx) * 0.5
        else:
            remaining = max(1, n_days - 1 - peak_center_idx)
            ct = 0.5 + ((i - peak_center_idx) / remaining) * 0.5
        ct  = min(1.0, max(0.0, ct))
        col = _interp_bloom_color(ct)
        try:
            label = day.strftime("%-d")
        except ValueError:
            label = day.strftime("%d").lstrip("0") or "0"
        in_bv = best_s <= i <= best_e
        glow  = "0 0 10px 2px rgba(242,149,157,.6)" if in_bv else "none"

        cells_html += (
            f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;'
            f'gap:5px;min-width:0;position:relative;z-index:1;">'
            f'<div style="background:{col};width:100%;aspect-ratio:2/1;'
            f'border-radius:4px;box-shadow:{glow};"></div>'
            f'<div style="font:600 9px \'IBM Plex Mono\',monospace;color:#cfc6d6;'
            f'white-space:nowrap;text-align:center;">{label}</div>'
            f'</div>'
        )

    try:
        first_label       = first_bloom.strftime("%-d %b")
        peak_label        = f"{peak_start.strftime('%-d')} – {peak_end.strftime('%-d %b')}"
        visit_label       = f"{visit_start.strftime('%-d %b')} – {visit_end.strftime('%-d %b')}"
        hanafubuki_label  = f"{hanafubuki_start.strftime('%-d %b')} – {hanafubuki_end.strftime('%-d %b')}"
    except ValueError:
        first_label       = first_bloom.strftime("%d %b").lstrip("0")
        peak_label        = f"{peak_start.strftime('%d').lstrip('0')} – {peak_end.strftime('%d %b').lstrip('0')}"
        visit_label       = f"{visit_start.strftime('%d %b')} – {visit_end.strftime('%d %b')}"
        hanafubuki_label  = f"{hanafubuki_start.strftime('%d %b')} – {hanafubuki_end.strftime('%d %b')}"

    station_display = station_name.title()
    forecast_doy    = int(row["predicted_day_of_year"]) if pd.notna(row.get("predicted_day_of_year")) else None
    badge_html      = _early_late_badge(forecast_doy, hist_avg_doy) if forecast_doy else ""
    accuracy_html   = _accuracy_note(station_mae, global_mae)
    estimated_html  = _estimated_tag(prediction_status)

    return textwrap.dedent(f"""
    <style>
    @media (max-width: 640px) {{
        .forecast-stages {{ grid-template-columns: 1fr !important; gap: 0 !important; }}
        .forecast-stages > div + div {{ border-top: 1px solid rgba(255,255,255,.08); }}
    }}
    @media (min-width: 641px) and (max-width: 860px) {{
        .forecast-stages {{ grid-template-columns: 1fr 1fr !important; }}
    }}
    </style>
    <div style="border-top:1px solid rgba(255,255,255,.1);padding-top:30px;margin-top:50px;position:relative;">
        <div style="margin-bottom:34px;">
            <div style="font:500 12px/1 'IBM Plex Mono',monospace;letter-spacing:2px;color:#e69bb4;margin-bottom:18px;">
                予報 &mdash; The forecast{estimated_html}
            </div>
            <h2 style="font:300 28px/1.15 'Newsreader',serif;color:#f6f1f4;margin:0 0 16px;">
                This spring in <em style="font-style:italic;color:#ff8fa9;">{station_display}</em>, day by day.
            </h2>
            {badge_html}
        </div>

        <!-- calendar strip -->
        <div style="position:relative;display:flex;gap:2px;justify-content:space-between;align-items:flex-end;">
            <!-- best viewing window rectangle -->
            <div style="position:absolute;left:{bv_left};width:{bv_width};top:-3px;bottom:14px;
                border:2px solid rgba(255,255,255,1);border-radius:10px;pointer-events:none;
                box-shadow:0 0 4px 1px rgba(255,255,255,.9),0 0 14px 2px rgba(255,255,255,.4),inset 0 0 3px 0 rgba(255,255,255,.25);z-index:2;
                background:rgba(255,255,255,.06);"></div>
            {cells_html}
        </div>

        <!-- four stages -->
        <div class="forecast-stages" style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:1px;margin-top:24px;
            background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.08);
            border-radius:12px;overflow:hidden;">

            <div style="background:#181420;padding:18px 20px;">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                    <span style="width:9px;height:9px;border-radius:50%;background:#f9dddf;"></span>
                    <span style="font:600 14px/1 'Shippori Mincho',serif;color:#f4eff4;">
                        開花 <span style="font:500 12px 'Schibsted Grotesk',sans-serif;color:#948fa0;">First bloom</span>
                    </span>
                </div>
                <div style="font:300 28px/1 'Newsreader',serif;color:#f6f1f4;">{first_label}</div>
                <div style="font:300 13px/1.45 'Newsreader',serif;color:#948fa0;margin-top:8px;">
                    First light appears in the blossoms, quietly marking the season’s return.
                </div>
            </div>

            <div style="background:#181420;padding:18px 20px;">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                    <span style="width:9px;height:9px;border-radius:50%;background:#f2959d;
                        box-shadow:0 0 8px #f2959d;"></span>
                    <span style="font:600 14px/1 'Shippori Mincho',serif;color:#f2959d;">
                        満開 <span style="font:500 12px 'Schibsted Grotesk',sans-serif;color:#d99fb0;">Peak bloom</span>
                    </span>
                </div>
                <div style="font:300 28px/1 'Newsreader',serif;color:#f2959d;">{peak_label}</div>
                <div style="font:300 13px/1.45 'Newsreader',serif;color:#948fa0;margin-top:8px;">
                    Every tree glows at its fullest, all at once.
                </div>
            </div>

            <div style="background:#181420;padding:18px 20px;">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                    <div style="width:11px;height:11px;border:2px solid rgba(255,255,255,.8);
                        border-radius:2px;background:rgba(255,255,255,.08);
                        box-shadow:0 0 8px rgba(255,255,255,.2);"></div>
                    <span style="font:600 14px/1 'Shippori Mincho',serif;color:#f4eff4;">
                        見頃 <span style="font:500 12px 'Schibsted Grotesk',sans-serif;color:#948fa0;">Best viewing</span>
                    </span>
                </div>
                <div style="font:300 28px/1 'Newsreader',serif;color:#f6f1f4;">{visit_label}</div>
                <div style="font:300 13px/1.45 'Newsreader',serif;color:#948fa0;margin-top:8px;">
                    The luminous overlap of peak bloom and drifting petals.
                </div>
            </div>

            <div style="background:#181420;padding:18px 20px;">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                    <span style="width:9px;height:9px;border-radius:50%;
                        background:rgba(249,221,223,0.3);border:1px solid rgba(249,221,223,0.45);"></span>
                    <span style="font:600 14px/1 'Shippori Mincho',serif;color:#b8afc4;">
                        花吹雪 <span style="font:500 12px 'Schibsted Grotesk',sans-serif;color:#948fa0;">Petal drift</span>
                    </span>
                </div>
                <div style="font:300 28px/1 'Newsreader',serif;color:#b8afc4;">{hanafubuki_label}</div>
                <div style="font:300 13px/1.45 'Newsreader',serif;color:#948fa0;margin-top:8px;">
                    Loose petals fill the air in brief, luminous flurries before the season fades.
                </div>
            </div>

        </div>
        {accuracy_html}
    </div>
    """).strip()


def render_best_time_to_visit_card(
    station_name: str,
    forecast_df: pd.DataFrame,
) -> str:
    dates = get_best_visit_dates(forecast_df)

    if not dates["available"]:
        return textwrap.dedent(
            f"""
            <div class="best-visit-card">
                <h3>Best Time to Visit</h3>
                <p class="best-visit-subtitle">
                    No forecast available for this station.
                </p>
            </div>
            """
        ).strip()

    first_bloom = dates["first_bloom"]
    peak_start = dates["peak_start"]
    peak_end = dates["peak_end"]
    visit_start = dates["visit_start"]
    visit_end = dates["visit_end"]

    tick_1 = first_bloom
    tick_2 = visit_start + pd.Timedelta(days=2)
    tick_3 = peak_end + pd.Timedelta(days=1)
    tick_4 = visit_end + pd.Timedelta(days=2)

    first_bloom_label = format_inline_date(first_bloom)
    peak_range_label = format_range_compact(peak_start, peak_end)
    visit_range_label = format_range_compact(visit_start, visit_end)

    return textwrap.dedent(
        f"""
        <div class="best-visit-card">

            <h3>Best Time to Visit</h3>

            <div class="visit-timeline-labels">
                <div class="timeline-label label-first">
                    <span>
                        First<br>
                        bloom
                    </span>
                    <div class="dotted-line"></div>
                </div>

                <div class="timeline-label label-peak">
                    <span>
                        Peak<br>
                        bloom
                    </span>
                    <div class="dotted-line"></div>
                </div>

                <div class="timeline-label label-best">
                    <span>
                        Best time<br>
                        to visit
                    </span>
                    <div class="dotted-line"></div>
                </div>
            </div>

            <div class="visit-timeline-wrap">
                <div class="timeline-pale-track"></div>
                <div class="timeline-visit-window"></div>
                <div class="timeline-peak-window"></div>

                <div class="timeline-dot dot-first"></div>
                <div class="timeline-dot dot-peak"></div>
                <div class="timeline-dot dot-best"></div>
            </div>

            <div class="timeline-axis">
                <div class="axis-line"></div>

                <div class="axis-tick tick-one">
                    <div class="tick-mark"></div>
                    <div class="tick-date">{format_card_date(tick_1)}</div>
                </div>

                <div class="axis-tick tick-two">
                    <div class="tick-mark"></div>
                    <div class="tick-date">{format_card_date(tick_2)}</div>
                </div>

                <div class="axis-tick tick-three">
                    <div class="tick-mark"></div>
                    <div class="tick-date">{format_card_date(tick_3)}</div>
                </div>

                <div class="axis-tick tick-four">
                    <div class="tick-mark"></div>
                    <div class="tick-date">{format_card_date(tick_4)}</div>
                </div>
            </div>

            <div class="visit-detail-section">

                <div class="visit-detail-row">
                    <div class="visit-detail-dot"></div>
                    <div>
                        <div class="visit-detail-label">Estimated first bloom</div>
                        <div class="visit-detail-value">{first_bloom_label}</div>
                    </div>
                </div>

                <div class="visit-row-line"></div>                

                <div class="visit-detail-row">
                    <div class="visit-detail-dot bright"></div>
                    <div>
                        <div class="visit-detail-label">Estimated peak bloom</div>
                        <div class="visit-detail-value">{peak_range_label}</div>
                    </div>
                </div>

                <div class="visit-row-line"></div>

                <div class="visit-detail-row">
                    <div class="visit-detail-dot medium"></div>
                    <div>
                        <div class="visit-detail-label">Best time to visit</div>
                        <div class="visit-detail-value">{visit_range_label}</div>
                    </div>
                </div>

            </div>

        </div>
        """
    ).strip()