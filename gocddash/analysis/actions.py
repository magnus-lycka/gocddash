from gocddash.analysis import pipeline_fetcher, go_request, data_access


def pull(pipeline_name, subsequent_pipelines, start, dry_run):
    latest_pipeline = data_access.get_connection().get_highest_pipeline_count(pipeline_name)
    print("In pipeline: " + pipeline_name)
    max_pipeline_status, max_available_pipeline = go_request.get_max_pipeline_status(pipeline_name)
    print("Latest synced pipeline locally: " + str(latest_pipeline))
    print("Latest pipeline in GO: " + str(max_pipeline_status))
    print("Latest available pipeline: " + str(max_available_pipeline))

    pipeline_name, latest_pipeline, max_pipeline_status, subsequent_pipelines, start = assert_correct_input(
        pipeline_name, latest_pipeline, max_pipeline_status, subsequent_pipelines, max_available_pipeline, start=start)

    if not dry_run:
        fetch_pipelines(pipeline_name, latest_pipeline, max_pipeline_status, subsequent_pipelines, start)
        print("Done.")
    else:
        print("Dry run!")


def all_info():
    all_synced = data_access.get_connection().get_synced_pipelines()
    print("I have these pipelines: ")
    print("Pipeline \t\tLocal \tIn Go")
    for pipeline in all_synced:
        print("{}\t{}\t{}".format(pipeline[0], pipeline[1], go_request.get_max_pipeline_status(pipeline[0])[1]))


def info(pipeline_name):
    latest_pipeline = data_access.get_connection().get_highest_pipeline_count(pipeline_name)
    print("In pipeline: " + pipeline_name)
    print("Current pipeline counter in GO, latest available pipeline: " + str(
        go_request.get_max_pipeline_status(pipeline_name)))
    print("Latest synced pipeline locally: {}".format(latest_pipeline))


def assert_correct_input(pipeline_name, latest_pipeline, max_pipeline_status, subsequent_pipelines,
                         max_available_pipeline, start):
    if start == 0 and latest_pipeline >= go_request.get_max_pipeline_status(pipeline_name)[1]:
        print("Latest pipeline ({}) = Max available pipeline ({}). Database is up to date!"
              .format(latest_pipeline, max_available_pipeline))
        print("Terminating program.")
        raise SystemExit

    if start + subsequent_pipelines > max_pipeline_status:
        initial_subsequent_pipelines = subsequent_pipelines
        subsequent_pipelines = max_pipeline_status - start
        print("Max requested pipeline ({}) > Max pipeline in GO ({}). Fetching latest {} pipelines instead."
              .format(start + initial_subsequent_pipelines, max_pipeline_status, subsequent_pipelines))

    return pipeline_name, latest_pipeline, max_pipeline_status, subsequent_pipelines, start


def fetch_pipelines(pipeline_name, latest_pipeline, max_pipeline_status, subsequent_pipelines, start):
    offset, run_times = go_request.calculate_request(latest_pipeline, max_pipeline_status,
                                                     pipelines=subsequent_pipelines, start=start)
    pipeline_fetcher.download_and_store(pipeline_name, offset, run_times)
