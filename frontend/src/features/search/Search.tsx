import React from 'react'
import {IconButton, Input, InputGroup, InputLeftElement} from '@chakra-ui/react'
import { SearchIcon } from "@chakra-ui/icons";

type Props = {
  updateSearchTerms: (searchTerms: string) => void;
  isSearchingDisabled?: boolean;
};


export const Search: React.FC<Props> = ({
  updateSearchTerms,
  isSearchingDisabled,
}) => {
  const [searchTerms, setSearchTerms] = React.useState<string>("");
  const handleSearchTermsChange = (event: React.ChangeEvent<HTMLInputElement>) => setSearchTerms(event.target.value);
  const handleClickSearch = () => { updateSearchTerms(searchTerms) };

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
        onKeyDown={(event) => {if (event.key === 'Enter') {handleClickSearch()} }}
      />
    </InputGroup>
  )
}
