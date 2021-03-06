import os
import io
from zipfile import ZipFile
import shutil
import json
from modelhubapi_tests.mockmodels.contrib_src_si.inference import Model
from modelhubapi_tests.mockmodels.contrib_src_mi.inference import ModelNeedsTwoInputs
from .apitestbase import TestRESTAPIBase
from modelhubapi import ModelHubAPI



class TestModelHubRESTAPI_SI(TestRESTAPIBase):

    def setUp(self):
        self.this_dir = os.path.dirname(os.path.realpath(__file__))
        self.contrib_src_dir = os.path.join(self.this_dir, "mockmodels", "contrib_src_si")
        self.setup_self_temp_work_dir()
        self.setup_self_temp_output_dir()
        self.setup_self_test_client(Model(), self.contrib_src_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_work_dir, ignore_errors=True)
        shutil.rmtree(self.temp_output_dir, ignore_errors=True)
        pass

    def test_get_config_returns_correct_dict(self):
        response = self.client.get("/api/get_config")
        self.assertEqual(200, response.status_code)
        config = json.loads(response.get_data())
        self.assert_config_contains_correct_dict(config)


    def test_get_legal_returns_expected_keys(self):
        response = self.client.get("/api/get_legal")
        self.assertEqual(200, response.status_code)
        legal = json.loads(response.get_data())
        self.assert_legal_contains_expected_keys(legal)


    def test_get_legal_returns_expected_mock_values(self):
        response = self.client.get("/api/get_legal")
        self.assertEqual(200, response.status_code)
        legal = json.loads(response.get_data())
        self.assert_legal_contains_expected_mock_values(legal)


    def test_get_model_io_returns_expected_mock_values(self):
        response = self.client.get("/api/get_model_io")
        self.assertEqual(200, response.status_code)
        model_io = json.loads(response.get_data())
        self.assert_model_io_contains_expected_mock_values(model_io)


    def test_get_samples_returns_path_to_mock_samples(self):
        response = self.client.get("/api/get_samples")
        self.assertEqual(200, response.status_code)
        samples = json.loads(response.get_data())
        samples.sort()
        self.assertListEqual(["http://localhost/api/samples/testimage_ramp_4x2.jpg",
                              "http://localhost/api/samples/testimage_ramp_4x2.png"],
                             samples)


    def test_samples_routes_correct(self):
        response = self.client.get("/api/samples/testimage_ramp_4x2.png")
        self.assertEqual(200, response.status_code)
        self.assertEqual("image/png", response.content_type)


    def test_thumbnail_routes_correct(self):
        response = self.client.get("/api/thumbnail/thumbnail.jpg")
        self.assertEqual(200, response.status_code)
        self.assertEqual("image/jpeg", response.content_type)


    def test_get_model_files_returns_zip(self):
        response = self.client.get("/api/get_model_files")
        self.assertEqual(200, response.status_code)
        self.assertEqual("application/zip", response.content_type)


    def test_get_model_files_returned_zip_has_mock_content(self):
        response = self.client.get("/api/get_model_files")
        self.assertEqual(200, response.status_code)
        test_zip_name = self.temp_work_dir + "/test_response.zip"
        with open(test_zip_name, "wb") as test_file:
            test_file.write(response.get_data())
        with ZipFile(test_zip_name, "r") as test_zip:
            reference_content = ["model/",
                                 "model/model.txt",
                                 "model/config.json",
                                 "model/thumbnail.jpg"]
            reference_content.sort()
            zip_content = test_zip.namelist()
            zip_content.sort()
            self.assertListEqual(reference_content, zip_content)
            self.assertEqual(b"EMPTY MOCK MODEL FOR UNIT TESTING",
                             test_zip.read("model/model.txt"))


    def test_predict_by_post_returns_expected_mock_prediction(self):
        response = self._post_predict_request_on_sample_image("testimage_ramp_4x2.png")
        self.assertEqual(200, response.status_code)
        result = json.loads(response.get_data())
        self.assert_predict_contains_expected_mock_prediction(result)


    def test_predict_by_post_returns_expected_mock_meta_info(self):
        response = self._post_predict_request_on_sample_image("testimage_ramp_4x2.png")
        self.assertEqual(200, response.status_code)
        result = json.loads(response.get_data())
        self.assert_predict_contains_expected_mock_meta_info(result)


    def test_predict_by_post_returns_error_on_unsupported_file_type(self):
        response = self._post_predict_request_on_sample_image("testimage_ramp_4x2.jpg")
        self.assertEqual(400, response.status_code)
        result = json.loads(response.get_data())
        self.assertIn("error", result)
        self.assertIn("Incorrect file type.", result["error"])


    def test_working_folder_empty_after_predict_by_post(self):
        response = self._post_predict_request_on_sample_image("testimage_ramp_4x2.png")
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(os.listdir(self.temp_work_dir) ), 0)


    # TODO this is not so nice yet, test should not require a download from the inet
    # should probably use a mock server for this
    def test_predict_by_url_returns_expected_mock_prediction(self):
        response = self.client.get("/api/predict?fileurl=https://raw.githubusercontent.com/modelhub-ai/modelhub-docker/master/framework/modelhublib_tests/testdata/testimage_ramp_4x2.png")
        self.assertEqual(200, response.status_code)
        result = json.loads(response.get_data())
        self.assert_predict_contains_expected_mock_prediction(result)


    # TODO this is not so nice yet, test should not require a download from the inet
    # should probably use a mock server for this
    def test_predict_by_url_returns_expected_mock_meta_info(self):
        response = self.client.get("/api/predict?fileurl=https://raw.githubusercontent.com/modelhub-ai/modelhub-docker/master/framework/modelhublib_tests/testdata/testimage_ramp_4x2.png")
        self.assertEqual(200, response.status_code)
        result = json.loads(response.get_data())
        self.assert_predict_contains_expected_mock_meta_info(result)


    # TODO this is not so nice yet, test should not require a download from the inet
    # should probably use a mock server for this
    def test_predict_by_url_returns_error_on_unsupported_file_type(self):
        response = self.client.get("/api/predict?fileurl=https://raw.githubusercontent.com/modelhub-ai/modelhub-docker/master/framework/modelhublib_tests/testdata/testimage_ramp_4x2.jpg")
        self.assertEqual(400, response.status_code)
        result = json.loads(response.get_data())
        self.assertIn("error", result)
        self.assertIn("Incorrect file type.", result["error"])


    def test_working_folder_empty_after_predict_by_url(self):
        response = self.client.get("/api/predict?fileurl=https://raw.githubusercontent.com/modelhub-ai/modelhub-docker/master/framework/modelhublib_tests/testdata/testimage_ramp_4x2.png")
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(os.listdir(self.temp_work_dir) ), 0)


    def test_predict_sample_returns_expected_mock_prediction(self):
        response = self.client.get("/api/predict_sample?filename=testimage_ramp_4x2.png")
        self.assertEqual(200, response.status_code)
        result = json.loads(response.get_data())
        self.assert_predict_contains_expected_mock_prediction(result)


    def test_predict_sample_on_invalid_file_returns_error(self):
        response = self.client.get("/api/predict_sample?filename=NON_EXISTENT.png")
        self.assertEqual(400, response.status_code)

class TestModelHubRESTAPI_MI(TestRESTAPIBase):

    def setUp(self):
        self.this_dir = os.path.dirname(os.path.realpath(__file__))
        self.contrib_src_dir = os.path.join(self.this_dir, "mockmodels", "contrib_src_mi")
        self.setup_self_temp_work_dir()
        self.setup_self_temp_output_dir()
        self.setup_self_test_client(ModelNeedsTwoInputs(), self.contrib_src_dir)
        self.client.api = ModelHubAPI(ModelNeedsTwoInputs(), self.contrib_src_dir)
        self.client.api.get_config = self.monkeyconfig()

    def tearDown(self):
        shutil.rmtree(self.temp_work_dir, ignore_errors=True)
        shutil.rmtree(self.temp_output_dir, ignore_errors=True)
        pass

    # this can change the config on the fly
    def monkeyconfig(self):
        return self.client.api._load_json(self.contrib_src_dir + '/model/config_4_nii.json')

    def test_get_config_returns_correct_dict(self):
        response = self.client.get("/api/get_config")
        self.assertEqual(200, response.status_code)
        config = json.loads(response.get_data())
        self.assert_config_contains_correct_dict(config)

    # TODO this is not so nice yet, test should not require a download from the inet
    # should probably use a mock server for this
    def test_working_folder_empty_after_predict_by_url(self):
        response = self.client.get("/api/predict?fileurl=https://raw.githubusercontent.com/modelhub-ai/modelhub-engine/master/framework/modelhubapi_tests/mockmodels/contrib_src_mi/sample_data/4_nii_gz_url.json")
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(os.listdir(self.temp_work_dir) ), 0)

    # TODO this is not so nice yet, test should not require a download from the inet
    # should probably use a mock server for this
    def test_api_downloads_files_from_url(self):
        response = self.client.get("/api/predict?fileurl=https://raw.githubusercontent.com/modelhub-ai/modelhub-engine/master/framework/modelhubapi_tests/mockmodels/contrib_src_mi/sample_data/4_nii_gz_url.json")
        self.assertEqual(200, response.status_code)

    # TODO this is not so nice yet, test should not require a download from the inet
    # should probably use a mock server for this
    def test_api_manages_mix_of_url_and_local_paths(self):
        response = self.client.get("/api/predict?fileurl=https://raw.githubusercontent.com/modelhub-ai/modelhub-engine/master/framework/modelhubapi_tests/mockmodels/contrib_src_mi/sample_data/4_nii_gz_mixed.json")
        self.assertEqual(200, response.status_code)

    # TODO this is not so nice yet, test should not require a download from the inet
    # should probably use a mock server for this
    def test_api_rejects_wrong_url_in_json(self):
        response = self.client.get("/api/predict?fileurl=https://raw.githubusercontent.com/modelhub-ai/modelhub-engine/master/framework/modelhubapi_tests/mockmodels/contrib_src_mi/sample_data/4_nii_gz_url_error.json")
        self.assertEqual(400, response.status_code)
        result = json.loads(response.get_data())
        self.assertIn("error", result)

    def test_api_fails_on_config_mismatch(self):
        response = self.client.get("/api/predict?fileurl=https://raw.githubusercontent.com/modelhub-ai/modelhub-engine/master/framework/modelhubapi_tests/mockmodels/contrib_src_mi/sample_data/missing_key.json")
        self.assertEqual(400, response.status_code)
        result = json.loads(response.get_data())
        self.assertIn("error", result)

if __name__ == '__main__':
    unittest.main()