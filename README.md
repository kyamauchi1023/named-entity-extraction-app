# SET UP SERVER

## Poetryを用いたセットアップ

```shell
$ poetry install  # パッケージをインストール
$ poetry shell
$ poetry run uvicorn server.main:app --host 0.0.0.0 --reload  # サーバーを立ち上げ
```

[http://localhost:8000/docs](http://localhost:8000/docs)にアクセスすると自動生成されたOAS(ドキュメント)が確認できる

---

## Docker+Poetryを用いたセットアップ

### 0. Docker Hubの登録とDockerのインストール
まずは、[Docker Hub](https://hub.docker.com/)のアカウント登録を行い、DockerおよびDocker Composeをインストールする（[参考](https://datawokagaku.com/startdocker/)）

  1. [Docker Hub](https://hub.docker.com/)にアクセスし、Sign Upフォームに記入をすると、Address verificationのメールが送られてくるので、Verifyする

  2. Login後、'Get started with Docker Desktop' → ‘Download Docker Desktop for Mac（Windows）’の順にクリックし、Docker Desktopをダウンロードする（Docker Desktopをダウンロードすると、Docker本体と同時にDocker EngineやDocker Composeなどもインストールすることができます）

  3. インストールが終わり次第、Docker Engineを起動させ、シェルで`docker login`コマンドを実行しログインをする


### 1. Dockerイメージをビルド（imageがない場合のみ）
```shell
$ docker-compose build
```

### 2. `poetry init`コマンドで`pyproject.toml`を作成（`pyproject.toml`がない場合のみ）
```shell
$ docker-compose run --rm \
  --entrypoint "poetry init \
    --name demo-app \
    --dependency fastapi \
    --dependency uvicorn[standard]" \
  demo-app
```
インタラクティブなダイアログでは、Authorのパートのみ`n`を入力し、それ以外では`Enter`を入力

### 3. パッケージをインストール
Docker imageをビルドし直したり、`.dockervenv`を作り直したときは以下を実行
```shell
$ docker-compose run --rm --entrypoint "poetry install" demo-app
```

### 4. コンテナの立ち上げ
```shell
$ docker-compose up -d
```
[http://localhost:8000/docs](http://localhost:8000/docs)にアクセスすると自動生成されたOASが確認できる

### 5. 追加でパッケージをインストール
新しいPythonパッケージを追加したい場合などは以下のように`pyproject.toml`を更新
```shell
$ docker-compose run --rm --entrypoint "poetry add [package1] [package2] ..." demo-app
```
なお、開発用でのみ必要なライブラリは`-D`オプションを付けてインストールする
```shell
$ docker-compose run --rm --entrypoint "poetry add -D [package1] [package2] ..." demo-app
```

### 6. コンテナを必要に応じて削除
```shell
$ docker-compose down
```
