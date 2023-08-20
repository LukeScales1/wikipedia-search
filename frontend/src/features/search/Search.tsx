import React from 'react'
import {IconButton, Input, InputGroup, InputLeftElement} from '@chakra-ui/react'
import { SearchIcon } from "@chakra-ui/icons";
import { useGetArticlesQuery } from "../../redux/apiSlice";

type Props = {
  updateSearchTerms: (searchTerms: string) => void;
};


export const Search: React.FC<Props> = ({
  updateSearchTerms,
}) => {
  const { error, isLoading } = useGetArticlesQuery('');

  const [searchTerms, setSearchTerms] = React.useState<string>("");
  const handleSearchTermsChange = (event: React.ChangeEvent<HTMLInputElement>) => setSearchTerms(event.target.value);
  const handleClickSearch = () => { updateSearchTerms(searchTerms) };

  const isSearchingDisabled = error ? true : isLoading;

  return (
    <InputGroup width={"60%"} marginBottom={"8px"}>
      <InputLeftElement>
        <IconButton
          aria-label='Search articles'
          icon={<SearchIcon />}
          onClick={handleClickSearch}
          isDisabled={isSearchingDisabled}
        />
      </InputLeftElement>
      <Input
        placeholder='Search your articles...'
        textAlign={"center"}
        value={searchTerms}
        onChange={handleSearchTermsChange}
        isDisabled={isSearchingDisabled}
      />
    </InputGroup>
  )
}