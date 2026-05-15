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


def render_best_time_to_visit_card(
    station_name: str,
    forecast_df: pd.DataFrame,
) -> str:
    dates = get_best_visit_dates(forecast_df)

    if not dates["available"]:
        return textwrap.dedent(
            f"""
            <div class="best-visit-card">
                <h3>Best time to visit {station_name.title()}</h3>
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

            <h3>Best time to visit {station_name.title()}</h3>

            <div class="visit-timeline-labels">
                <div class="timeline-label label-first">
                    <span>First bloom</span>
                    <div class="dotted-line"></div>
                </div>

                <div class="timeline-label label-peak">
                    <span>Peak bloom</span>
                    <div class="dotted-line"></div>
                </div>

                <div class="timeline-label label-best">
                    <span>Best time to visit</span>
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