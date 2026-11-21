import plotly.graph_objects as go


def crear_figura_pareto(df_grid, df_pareto, knee_point):
    fig = go.Figure()

    df_fact = df_grid[df_grid["factible"]]
    df_infact = df_grid[~df_grid["factible"]]

    fig.add_trace(
        go.Scatter(
            x=df_infact["Q_horno_kW"],
            y=df_infact["Xs"] * 100,
            mode="markers",
            name="Infactibles (S<sub>out</sub> > 10)",
            marker=dict(color="#B45309", size=4, opacity=0.6),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_fact["Q_horno_kW"],
            y=df_fact["Xs"] * 100,
            mode="markers",
            name="Factibles",
            marker=dict(color="#0E7490", size=4, opacity=0.8),
            hovertemplate=(
                "Q<sub>horno</sub>: %{x:.1f} kW<br>"
                "X<sub>s</sub>: %{y:.2f}%<br>"
                "T<sub>in</sub>: %{customdata[0]:.1f} K<br>"
                "ε: %{customdata[1]:.2f}<extra></extra>"
            ),
            customdata=df_fact[["Tin_K", "epsilon"]].values,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_pareto["Q_horno_kW"],
            y=df_pareto["Xs"] * 100,
            mode="lines+markers",
            name="Frontera de Pareto",
            line=dict(color="#1E3A8A", width=3),
            marker=dict(color="#1E3A8A", size=6),
            hovertemplate=(
                "<b>Pareto</b><br>"
                "Q<sub>horno</sub>: %{x:.1f} kW<br>"
                "X<sub>s</sub>: %{y:.2f}%<br>"
                "T<sub>in</sub>: %{customdata[0]:.1f} K<br>"
                "ε: %{customdata[1]:.2f}<extra></extra>"
            ),
            customdata=df_pareto[["Tin_K", "epsilon"]].values,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[knee_point["Q_horno_kW"]],
            y=[knee_point["Xs"] * 100],
            mode="markers",
            name="Knee Point",
            marker=dict(
                color="#EF4444",
                size=14,
                symbol="circle",
                line=dict(color="black", width=2),
            ),
            hovertemplate=(
                "<b>Knee Point</b><br>"
                "Q<sub>horno</sub>: %{x:.1f} kW<br>"
                "X<sub>s</sub>: %{y:.2f}%<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=dict(
            text="Optimización Multiobjetivo",
            x=0.5,
            xanchor="center",
            xref="paper",
        )
        xaxis_title="Carga Térmica Q<sub>horno</sub> (kW)",
        yaxis_title="Conversión X<sub>s</sub> (%)",
        font=dict(color="black", size=13),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255, 255, 255, 0.8)",
        ),
        height=500,
        margin=dict(b=100),
    )

    return fig
