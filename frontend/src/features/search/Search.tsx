import React from 'react'
import {IconButton, Input, InputGroup, InputLeftElement} from '@chakra-ui/react'
import { SearchIcon } from "@chakra-ui/icons";

export const Search = () => {

  const handleClickSearch = () => { console.log("Search") };

  return (
    <InputGroup width={"60%"} marginBottom={"8px"}>
      <InputLeftElement>
        <IconButton aria-label='Search articles' icon={<SearchIcon />} onClick={handleClickSearch}/>
      </InputLeftElement>
      <Input placeholder='Search your articles...' textAlign={"center"} />
    </InputGroup>
  )
}