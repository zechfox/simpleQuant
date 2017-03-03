import { Component } from '@angular/core';
import { Strategy } from './strategy';
import { StrategyService } from './strategy.service';
import { OnInit } from '@angular/core';
import { Router } from '@angular/router';
import 'codemirror/mode/python/python';

@Component({
  selector: 'my-strategies',
  templateUrl: './strategies.component.html',
  styleUrls: [ './strategies.component.css' ]
})




export class StrategiesComponent implements OnInit{
  title = 'Tour of Strategies';
  selectedStrategy: Strategy;
  strategies: Strategy[];
  public html:string = `
    <span type="button" class="btn btn-primary"> Save </span>
    <span type="button" class="btn btn-primary"> Cancel </span>`;
  config:any = { lineNumbers: true, mode:"python" };
  strategyCode:any = '// ... some code !';
  cmInstance: any;

  constructor(private router: Router,
    private strategyService: StrategyService) { }
  onSelect(strategy: Strategy): void {
    this.selectedStrategy= strategy;
    this.getStrategySourceCode();
  }

  getStrategies(): void {
    this.strategyService.getStrategies().then(strategies => this.strategies = strategies);
  }

  getStrategySourceCode(): void {
    this.strategyService.getStrategySourceCode(this.selectedStrategy.name).then(sourceCode => this.strategyCode = sourceCode);
  }

  saveChange(): void {

  }

  discardChange(): void {

  }

  ngOnInit(): void {
    this.getStrategies();
  }

  gotoDetail(): void {
    this.router.navigate(['/strategy/detail', this.selectedStrategy.name]);
  }
}

