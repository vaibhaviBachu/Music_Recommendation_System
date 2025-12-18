from flask import Flask, render_template, Response, jsonify
from camera import VideoCamera, music_rec

app = Flask(__name__)

# Table headings
headings = ("Name", "Album", "Artist")

# Global dataframe (initialized lazily)
df1 = None


@app.route('/')
def index():
    """
    Home page:
    - Loads music recommendations only when page is accessed
    """
    global df1
    if df1 is None:
        df1 = music_rec().head(15)

    return render_template(
        'index.html',
        headings=headings,
        data=df1
    )


def gen(camera):
    """
    Video streaming generator
    """
    global df1
    while True:
        frame, df1 = camera.get_frame()
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n'
        )


@app.route('/video_feed')
def video_feed():
    """
    Video streaming route
    """
    return Response(
        gen(VideoCamera()),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/t')
def gen_table():
    """
    Endpoint to return updated recommendations as JSON
    """
    if df1 is None:
        return jsonify([])
    return df1.to_json(orient='records')


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

