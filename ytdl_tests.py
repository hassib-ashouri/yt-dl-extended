import unittest
from ytmusicapi import YTMusic
import main

class TestYTDL(unittest.TestCase):
    
    def test_is_left_contained_in_right(self):
        strigns_to_test = [("Barry Can't Swim","Kimbara","Barry Can’t Swim", "Kimbara")]
        for str1, str2, str3, str4 in strigns_to_test:
            print(f"Testing: ({str1},{str2}), ({str3},{str4})")
            self.assertTrue(main.is_left_contained_in_right(str1, str3))
            self.assertTrue(main.is_left_contained_in_right(str2, str4))


    # this is more of an integration test
    # this does not test the string equality of the search results inside get_valid_songs
    def test_getting_valid_songs(self):
        ytmusic = main.init_ytmusic()

        searchCriteria = "Adam Port-Move-Extended"
        print("Searching for: ", searchCriteria)

        artist, title = searchCriteria.split("-")[0:2]
        print("artist:", artist, "title:", title)

        results = ytmusic.search(searchCriteria, filter='songs')
        print("Found: ", len(results), " songs on yt music")

        valid_songs = main.get_valid_songs(results, artist, title)
        main.print_yt_songs(valid_songs)

        self.assertGreater(len(valid_songs), 0)

    def test_getting_extended_version(self):
        ytmusic = main.init_ytmusic()

        searchCriteria = "BADDIES ONLY-3 Malas-extended"
        print("Searching for: ", searchCriteria)

        artist, title = searchCriteria.split("-")[0:2]
        print("artist:", artist, "title:", title)

        results = ytmusic.search(searchCriteria, filter='songs')
        print("Found: ", len(results), " songs on yt music")

        valid_songs = main.get_valid_songs(results, artist, title)
        main.print_yt_songs(valid_songs)

        extended_song_i = main.get_extended_song(valid_songs)
        extended_song = valid_songs[extended_song_i]

        print(f"Extended song is (index {extended_song_i}):", main.get_yt_song_preview(extended_song))

        self.assertGreater(extended_song_i, -1)
        self.assertTrue("Extended" in extended_song['title'])
        self.assertTrue(artist in extended_song['artists'][0]['name'])
        self.assertTrue(title in extended_song['title'])

if __name__ == '__main__':
    unittest.main()
