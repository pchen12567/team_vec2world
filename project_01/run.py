from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html',
                           title='欢迎来到新闻言论提取器',
                           index_header='新闻人物言论自动提取器'
                           )


@app.route('/sample')
def sample():
    return render_template('sample.html',
                           title='示例',
                           sample_header='示例展示'
                           )


if __name__ == '__main__':
    app.run(debug=True)
