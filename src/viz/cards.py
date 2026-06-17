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


def get_best_visit_dates(forecast_df: pd.DataFrame) -> dict:
    if forecast_df.empty or pd.isna(forecast_df.iloc[0]["predicted_event_date"]):
        return {"available": False}

    first_bloom = pd.to_datetime(forecast_df.iloc[0]["predicted_event_date"])

    peak_start = first_bloom + pd.Timedelta(days=4)
    peak_end = first_bloom + pd.Timedelta(days=6)

    visit_start = peak_start - pd.Timedelta(days=2)
    visit_end = peak_end + pd.Timedelta(days=4)

    return {
        "available": True,
        "first_bloom": first_bloom,
        "peak_start": peak_start,
        "peak_end": peak_end,
        "visit_start": visit_start,
        "visit_end": visit_end,
    }


def _interp_bloom_color(t: float) -> str:
    """Interpolate yellow→pink→purple gradient (matches the map scale)."""
    stops = [
        (0.0,  (242, 230, 184)),
        (0.45, (255, 143, 169)),
        (0.60, (255,  60, 120)),
        (1.0,  ( 40,  20,  35)),
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


def render_forecast_section(station_name: str, forecast_df: pd.DataFrame) -> str:
    dates = get_best_visit_dates(forecast_df)
    if not dates["available"]:
        return ""

    first_bloom = dates["first_bloom"]
    peak_start  = dates["peak_start"]
    peak_end    = dates["peak_end"]
    visit_start = dates["visit_start"]
    visit_end   = dates["visit_end"]

    n_days = 17
    cal_days = [first_bloom + pd.Timedelta(days=i) for i in range(n_days)]

    # peak centre index (middle of peak window)
    peak_center_idx = ((peak_start + (peak_end - peak_start) / 2) - first_bloom).days

    best_s = max(0, (visit_start - first_bloom).days)
    best_e = min(n_days - 1, (visit_end - first_bloom).days)

    cell_pct = 100.0 / n_days
    bv_left  = f"{best_s * cell_pct:.1f}%"
    bv_width = f"{(best_e - best_s + 1) * cell_pct:.1f}%"

    cells_html = ""
    for i, day in enumerate(cal_days):
        dist   = abs(i - peak_center_idx)
        inten  = max(0.08, math.exp(-(dist / 3.2) ** 2))
        ct     = min(1.0, max(0.0, (i - 1) / (n_days - 4)))
        col    = _interp_bloom_color(ct)
        opac   = 0.2 + 0.8 * inten
        try:
            label = day.strftime("%-d")
        except ValueError:
            label = day.strftime("%d").lstrip("0") or "0"
        in_bv  = best_s <= i <= best_e
        glow   = "0 0 10px 2px rgba(255,143,169,.6)" if in_bv else f"0 0 5px 0px {col}"

        cells_html += (
            f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;'
            f'gap:5px;min-width:0;position:relative;z-index:1;">'
            f'<div style="background:{col};opacity:{opac:.2f};width:100%;aspect-ratio:1;'
            f'border-radius:4px;box-shadow:{glow};"></div>'
            f'<div style="font:600 9px \'IBM Plex Mono\',monospace;color:#cfc6d6;'
            f'white-space:nowrap;text-align:center;">{label}</div>'
            f'</div>'
        )

    try:
        first_label = first_bloom.strftime("%-d %b")
        peak_label  = f"{peak_start.strftime('%-d')} – {peak_end.strftime('%-d %b')}"
        visit_label = f"{visit_start.strftime('%-d %b')} – {visit_end.strftime('%-d %b')}"
    except ValueError:
        first_label = first_bloom.strftime("%d %b").lstrip("0")
        peak_label  = f"{peak_start.strftime('%d').lstrip('0')} – {peak_end.strftime('%d %b').lstrip('0')}"
        visit_label = f"{visit_start.strftime('%d %b')} – {visit_end.strftime('%d %b')}"

    station_display = station_name.title()

    return textwrap.dedent(f"""
    <div style="border-top:1px solid rgba(255,255,255,.1);padding-top:30px;margin-top:8px;position:relative;">
        <div style="margin-bottom:20px;">
            <div style="font:500 12px/1 'IBM Plex Mono',monospace;letter-spacing:2px;color:#e69bb4;margin-bottom:8px;">
                予報 &mdash; The forecast for {station_display}
            </div>
            <div style="font:400 15px/1.4 'Newsreader',serif;font-style:italic;color:#948fa0;">
                Daily bloom intensity through the season.
            </div>
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

        <!-- three stages -->
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1px;margin-top:24px;
            background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.08);
            border-radius:12px;overflow:hidden;">

            <div style="background:#181420;padding:18px 20px;">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                    <span style="width:9px;height:9px;border-radius:50%;background:#8FC89A;"></span>
                    <span style="font:600 14px/1 'Shippori Mincho',serif;color:#f4eff4;">
                        開花 <span style="font:500 12px 'Schibsted Grotesk',sans-serif;color:#948fa0;">First bloom</span>
                    </span>
                </div>
                <div style="font:300 28px/1 'Newsreader',serif;color:#f6f1f4;">{first_label}</div>
                <div style="font:300 13px/1.45 'Newsreader',serif;color:#948fa0;margin-top:8px;">
                    First light appears in the blossoms, quietly marking the season’s return.
                </div>
            </div>

            <div style="background:#1d1622;padding:18px 20px;">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                    <span style="width:9px;height:9px;border-radius:50%;background:#ff8fa9;
                        box-shadow:0 0 8px #ff8fa9;"></span>
                    <span style="font:600 14px/1 'Shippori Mincho',serif;color:#ff8fa9;">
                        満開 <span style="font:500 12px 'Schibsted Grotesk',sans-serif;color:#d99fb0;">Peak bloom</span>
                    </span>
                </div>
                <div style="font:300 28px/1 'Newsreader',serif;color:#ff8fa9;">{peak_label}</div>
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
        </div>
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