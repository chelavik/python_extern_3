import plotly.graph_objs as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from datetime import datetime
import re

from API_requests import get_weather_conditions
from errors import BadRequest, APIKeyError


# Преобразование данных в удобные для графиков списки
def prepare_data(days, lon, lat):
    forecast_data = get_weather_conditions(lat, lon)
    dates = [datetime.fromisoformat(forecast_data[i]['Date']).strftime('%Y-%m-%d') for i in range(days)]
    min_temps = [forecast_data[i]['Minimal Temperature'] for i in range(days)]
    max_temps = [forecast_data[i]['Maximal Temperature'] for i in range(days)]
    humidity = [forecast_data[i]['Humidity'] for i in range(days)]
    wind_speed = [forecast_data[i]['Wind Speed'] for i in range(days)]
    precipitation = [forecast_data[i]['Precipitation Probability'] for i in range(days)]
    return dates, min_temps, max_temps, humidity, wind_speed, precipitation


# Создаем приложение Dash
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Прогноз погоды"),

    # Ввод координат
    html.Div([
        html.Label("Начальная широта:"),
        dcc.Input(id='start-lat', type='text', placeholder='Пример: 1.1234', debounce=True),
        html.Label("Начальная долгота:"),
        dcc.Input(id='start-lon', type='text', placeholder='Пример: 1.1234', debounce=True),
        html.Label("Конечная широта:"),
        dcc.Input(id='end-lat', type='text', placeholder='Пример: 1.1234', debounce=True),
        html.Label("Конечная долгота:"),
        dcc.Input(id='end-lon', type='text', placeholder='Пример: 1.1234', debounce=True),
        html.Button('Получить прогноз', id='submit-button', n_clicks=0),
        html.Div(id='coordinate-validation', style={'color': 'red'})
    ]),

    html.Label("Выберите количество отображаемых дней:"),

    # Dropdown для выбора интервала прогноза
    dcc.Dropdown(
        id='forecast-interval',
        options=[
            {'label': '3 дня', 'value': 3},
            {'label': '5 дней', 'value': 5}
        ],
        value=3  # значение по умолчанию
    ),

    # Вкладки для отображения графиков по городам
    dcc.Tabs(id='city-tabs', value='City1', children=[
        dcc.Tab(label='Город 1', value='City1'),
        dcc.Tab(label='Город 2', value='City2'),
    ]),

    # Контейнер для графиков
    html.Div(id='graphs-container')
])


# Валидация координат
def validate_coordinates(lat, lon):
    pattern = r'^-?\d+\.\d+$'
    return re.match(pattern, lat) and re.match(pattern, lon)


# Callback для обновления графиков и валидации координат
@app.callback(
    [Output('graphs-container', 'children'),
     Output('coordinate-validation', 'children')],
    [Input('forecast-interval', 'value'),
     Input('submit-button', 'n_clicks'),
     Input('start-lat', 'value'),
     Input('start-lon', 'value'),
     Input('end-lat', 'value'),
     Input('end-lon', 'value'),
     Input('city-tabs', 'value')]
)
def update_graphs(selected_days, n_clicks, start_lat, start_lon, end_lat, end_lon, active_tab):
    if n_clicks > 0:
        # Проверка на валидность координат
        if not all([start_lat, start_lon, end_lat, end_lon]) or not (validate_coordinates(start_lat, start_lon) and
                validate_coordinates(end_lat, end_lon)):
            return html.Div("Пожалуйста, введите действительные координаты в формате 1.1234", style={'color': 'red'}), ""

        # Создаем контейнер для графиков
        graphs = []

        # Обработка для начальных координат
        try:
            dates, min_temps, max_temps, humidity, wind_speed, precipitation = prepare_data(selected_days, start_lon, start_lat)

            # График температур
            temp_fig = go.Figure()
            temp_fig.add_trace(go.Scatter(x=dates, y=min_temps, mode='lines+markers', name='Минимальная температура'))
            temp_fig.add_trace(go.Scatter(x=dates, y=max_temps, mode='lines+markers', name='Максимальная температура'))
            temp_fig.update_layout(title="Город 1: Прогноз температуры", xaxis_title="Дата", yaxis_title="Температура (°C)")

            # График влажности
            humidity_fig = go.Figure()
            humidity_fig.add_trace(go.Bar(x=dates, y=humidity, name='Humidity'))
            humidity_fig.update_layout(title="Город 1: Прогноз влажности", xaxis_title="Дата", yaxis_title="Влажность (%)")

            # График скорости ветра
            wind_fig = go.Figure()
            wind_fig.add_trace(go.Bar(x=dates, y=wind_speed, name='Скорость ветра', marker_color='blue'))
            wind_fig.update_layout(title="Город 1: Прогноз скорости ветра", xaxis_title="Дата", yaxis_title="Скорость ветра (км/ч)")

            # График вероятности осадков
            precip_fig = go.Figure()
            precip_fig.add_trace(go.Scatter(x=dates, y=precipitation, mode='lines+markers', name='Вероятность осадков',
                                             marker_color='purple'))
            precip_fig.update_layout(title="Город 1: Прогноз вероятности осадков", xaxis_title="Дата", yaxis_title="Вероятность (%)")

            # Добавление графиков для Город 1 в контейнер
            if active_tab == 'City1':
                graphs.extend([
                    dcc.Graph(figure=temp_fig),
                    dcc.Graph(figure=humidity_fig),
                    dcc.Graph(figure=wind_fig),
                    dcc.Graph(figure=precip_fig),
                ])

        except (BadRequest, APIKeyError) as e:
            return html.Div(f"Ошибка при получении данных для начальных координат: {str(e)}", style={'color': 'red'}), ""
        except Exception as e:
            return html.Div(f"Непредвиденная ошибка при получении данных для начальных координат: {str(e)}", style={'color': 'red'}), ""

        # Обработка для конечных координат
        try:
            dates, min_temps, max_temps, humidity, wind_speed, precipitation = prepare_data(selected_days, end_lon, end_lat)

            # График температур
            temp_fig = go.Figure()
            temp_fig.add_trace(go.Scatter(x=dates, y=min_temps, mode='lines+markers', name='Минимальная температура'))
            temp_fig.add_trace(go.Scatter(x=dates, y=max_temps, mode='lines+markers', name='Максимальная температура'))
            temp_fig.update_layout(title="Город 2: Прогноз температуры", xaxis_title="Дата", yaxis_title="Температура (°C)")

            # График влажности
            humidity_fig = go.Figure()
            humidity_fig.add_trace(go.Bar(x=dates, y=humidity, name='Humidity'))
            humidity_fig.update_layout(title="Город 2: Прогноз влажности", xaxis_title="Дата", yaxis_title="Влажность (%)")

            # График скорости ветра
            wind_fig = go.Figure()
            wind_fig.add_trace(go.Bar(x=dates, y=wind_speed, name='Скорость ветра', marker_color='blue'))
            wind_fig.update_layout(title="Город 2: Прогноз скорости ветра", xaxis_title="Дата", yaxis_title="Скорость ветра (км/ч)")

            # График вероятности осадков
            precip_fig = go.Figure()
            precip_fig.add_trace(go.Scatter(x=dates, y=precipitation, mode='lines+markers', name='Вероятность осадков',
                                             marker_color='purple'))
            precip_fig.update_layout(title="Город 2: Прогноз вероятности осадков", xaxis_title="Дата", yaxis_title="Вероятность (%)")

            # Добавление графиков для Город 2 в контейнер
            if active_tab == 'City2':
                graphs.extend([
                    dcc.Graph(figure=temp_fig),
                    dcc.Graph(figure=humidity_fig),
                    dcc.Graph(figure=wind_fig),
                    dcc.Graph(figure=precip_fig),
                ])

        except (BadRequest, APIKeyError) as e:
            return html.Div(f"Ошибка при получении данных для конечных координат: {str(e)}", style={'color': 'red'}), ""

        except Exception as e:
            return html.Div(f"Непредвиденная ошибка при получении данных для конечных координат: {str(e)}", style={'color': 'red'}), ""
        return html.Div(graphs), ""

    # Если кнопка не нажата, возвращаем пустое сообщение
    return html.Div("Нажмите 'Получить прогноз' для отображения графиков"), ""


# Запуск приложения
if __name__ == '__main__':
    app.run_server(debug=True)
